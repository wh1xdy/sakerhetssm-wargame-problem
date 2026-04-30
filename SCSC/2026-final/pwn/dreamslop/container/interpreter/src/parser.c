#include "parser.h"

typedef struct {
    Lexer L;
    Tok   cur;
    Tok   lookahead;
    int   have_la;
} Par;

static Node *new_node(NKind k, int line) {
    Node *n = xcalloc(1, sizeof *n);
    n->kind = k;
    n->line = line;
    return n;
}

static void p_advance(Par *p) {
    if (p->have_la) { p->cur = p->lookahead; p->have_la = 0; }
    else p->cur = lex_next(&p->L);
}

static Tok p_peek(Par *p) {
    if (!p->have_la) { p->lookahead = lex_next(&p->L); p->have_la = 1; }
    return p->lookahead;
}

static int p_check(Par *p, TokKind k) { return p->cur.kind == k; }

static int p_match(Par *p, TokKind k) {
    if (p->cur.kind == k) { p_advance(p); return 1; }
    return 0;
}

/* Lenient version of p_expect: closers (), ], }, INTERP_END) at EOF are
 * silently inserted thanks to ABI (Automatic-Bracket-Insertion). Other
 * mismatches still error. */
static void p_expect(Par *p, TokKind k, const char *what) {
    if (p->cur.kind == k) { p_advance(p); return; }
    if (p->cur.kind == TK_EOF &&
        (k == TK_RPAREN || k == TK_RBRACKET || k == TK_RBRACE || k == TK_INTERP_END))
        return; /* ABI: pretend the closer was here */
    db_error("parse: expected %s, got %s at line %d", what, tok_name(p->cur.kind), p->cur.line);
}

/* Forward declarations */
static Node *parse_stmt(Par *p);
static Node *parse_expr(Par *p);
static Node *parse_block(Par *p);
static Node *parse_assign_or_expr(Par *p);

/* Array utility */
static void push_node(Node ***buf, int *n, int *cap, Node *x) {
    if (*n + 1 > *cap) {
        *cap = *cap ? *cap * 2 : 4;
        *buf = xrealloc(*buf, (size_t)*cap * sizeof **buf);
    }
    (*buf)[(*n)++] = x;
}

/* Primary: literals, identifiers, parens, arrays, objects, lambdas, templates, new, previous, next */
static Node *parse_primary(Par *p) {
    Tok t = p->cur;
    switch (t.kind) {
    case TK_NUM: {
        p_advance(p);
        Node *n = new_node(N_LIT_NUM, t.line);
        n->u.num = t.num;
        return n;
    }
    case TK_STR: {
        p_advance(p);
        Node *n = new_node(N_LIT_STR, t.line);
        n->u.str.data = t.text;
        n->u.str.len  = t.len;
        return n;
    }
    case TK_STR_CHUNK: {
        /* Template: alternating chunks and expressions. */
        Node *tmpl = new_node(N_TEMPLATE, t.line);
        Node **items = NULL; int n = 0, cap = 0;
        Node *first = new_node(N_LIT_STR, t.line);
        first->u.str.data = t.text;
        first->u.str.len  = t.len;
        push_node(&items, &n, &cap, first);
        p_advance(p);
        while (p->cur.kind == TK_INTERP_START) {
            p_advance(p);
            Node *e = parse_expr(p);
            push_node(&items, &n, &cap, e);
            if (p->cur.kind != TK_INTERP_END)
                db_error("parse: expected '}' to close string interpolation at line %d", p->cur.line);
            p_advance(p);
            if (p->cur.kind == TK_STR_CHUNK) {
                Node *c = new_node(N_LIT_STR, p->cur.line);
                c->u.str.data = p->cur.text;
                c->u.str.len  = p->cur.len;
                push_node(&items, &n, &cap, c);
                p_advance(p);
            } else {
                break;
            }
        }
        tmpl->u.arr.items = items;
        tmpl->u.arr.n     = n;
        return tmpl;
    }
    case TK_TRUE:
    case TK_FALSE:
    case TK_MAYBE: {
        Node *n = new_node(N_LIT_BOOL, t.line);
        n->u.boolv = t.kind == TK_TRUE ? B_TRUE : t.kind == TK_FALSE ? B_FALSE : B_MAYBE;
        p_advance(p);
        return n;
    }
    case TK_UNDEFINED: {
        p_advance(p);
        return new_node(N_LIT_UNDEF, t.line);
    }
    case TK_PREVIOUS: {
        p_advance(p);
        if (p->cur.kind != TK_IDENT) db_error("parse: expected identifier after 'previous' at line %d", p->cur.line);
        Node *n = new_node(N_PREVIOUS, t.line);
        n->u.prev.name = p->cur.text;
        p_advance(p);
        return n;
    }
    case TK_NEXT: {
        p_advance(p);
        if (p->cur.kind != TK_IDENT) db_error("parse: expected identifier after 'next' at line %d", p->cur.line);
        Node *n = new_node(N_NEXT, t.line);
        n->u.nxt.name = p->cur.text;
        p_advance(p);
        return n;
    }
    case TK_NEW: {
        p_advance(p);
        if (p->cur.kind != TK_IDENT && p->cur.kind != TK_CLASS) /* allow 'new ClassName' */
            db_error("parse: expected class name after 'new' at line %d", p->cur.line);
        char *name = p->cur.text;
        p_advance(p);
        p_expect(p, TK_LPAREN, "(");
        Node **args = NULL; int n = 0, cap = 0;
        if (!p_check(p, TK_RPAREN)) {
            do { push_node(&args, &n, &cap, parse_expr(p)); } while (p_match(p, TK_COMMA));
        }
        p_expect(p, TK_RPAREN, ")");
        Node *nn = new_node(N_NEW, t.line);
        nn->u.newc.name = name;
        nn->u.newc.args = args;
        nn->u.newc.nargs = n;
        return nn;
    }
    case TK_IDENT: {
        p_advance(p);
        Node *n = new_node(N_IDENT, t.line);
        n->u.ident.name = t.text;
        return n;
    }
    case TK_LPAREN: {
        p_advance(p);
        /* Empty parens: '() => body' is a zero-arg lambda. */
        if (p->cur.kind == TK_RPAREN) {
            p_advance(p);
            if (p->cur.kind == TK_ARROW) {
                p_advance(p);
                Node *lam = new_node(N_LAMBDA, t.line);
                lam->u.fn.params  = NULL;
                lam->u.fn.nparams = 0;
                if (p->cur.kind == TK_LBRACE) lam->u.fn.body = parse_block(p);
                else {
                    Node *blk = new_node(N_BLOCK, p->cur.line);
                    Node **stmts = NULL; int sn = 0, scap = 0;
                    Node *ret = new_node(N_RETURN, p->cur.line);
                    ret->u.ret.val = parse_expr(p);
                    push_node(&stmts, &sn, &scap, ret);
                    blk->u.block.stmts = stmts;
                    blk->u.block.n = sn;
                    lam->u.fn.body = blk;
                }
                return lam;
            }
            db_error("parse: empty parens at line %d", t.line);
        }
        /* Parse a comma-separated list. If followed by '=>', it's a lambda
         * parameter list; otherwise it must be a single expression. */
        Node **items = NULL; int n = 0, cap = 0;
        push_node(&items, &n, &cap, parse_expr(p));
        while (p_match(p, TK_COMMA)) push_node(&items, &n, &cap, parse_expr(p));
        p_expect(p, TK_RPAREN, ")");
        if (p->cur.kind == TK_ARROW) {
            p_advance(p);
            Node *lam = new_node(N_LAMBDA, t.line);
            Node **params = xmalloc((size_t)n * sizeof *params);
            for (int i = 0; i < n; i++) {
                if (items[i]->kind != N_IDENT)
                    db_error("parse: lambda parameters must be identifiers at line %d", t.line);
                params[i] = items[i];
            }
            free(items);
            lam->u.fn.params  = params;
            lam->u.fn.nparams = n;
            if (p->cur.kind == TK_LBRACE) lam->u.fn.body = parse_block(p);
            else {
                Node *blk = new_node(N_BLOCK, p->cur.line);
                Node **stmts = NULL; int sn = 0, scap = 0;
                Node *ret = new_node(N_RETURN, p->cur.line);
                ret->u.ret.val = parse_expr(p);
                push_node(&stmts, &sn, &scap, ret);
                blk->u.block.stmts = stmts;
                blk->u.block.n = sn;
                lam->u.fn.body = blk;
            }
            return lam;
        }
        if (n != 1)
            db_error("parse: comma-separated expressions outside a function call at line %d", t.line);
        Node *only = items[0];
        free(items);
        return only;
    }
    case TK_LBRACKET: {
        p_advance(p);
        Node *n = new_node(N_ARRAY, t.line);
        Node **items = NULL; int cnt = 0, cap = 0;
        if (!p_check(p, TK_RBRACKET)) {
            do { push_node(&items, &cnt, &cap, parse_expr(p)); } while (p_match(p, TK_COMMA));
        }
        p_expect(p, TK_RBRACKET, "]");
        n->u.arr.items = items;
        n->u.arr.n     = cnt;
        return n;
    }
    case TK_LBRACE: {
        /* Object literal */
        p_advance(p);
        Node *n = new_node(N_OBJECT, t.line);
        char **keys = NULL; Node **vals = NULL; int cnt = 0, cap = 0;
        if (!p_check(p, TK_RBRACE)) {
            do {
                char *k;
                if (p->cur.kind == TK_IDENT || p->cur.kind == TK_STR) k = p->cur.text;
                else db_error("parse: expected object key at line %d", p->cur.line);
                p_advance(p);
                p_expect(p, TK_COLON, ":");
                Node *v = parse_expr(p);
                if (cnt + 1 > cap) {
                    cap = cap ? cap * 2 : 4;
                    keys = xrealloc(keys, (size_t)cap * sizeof *keys);
                    vals = xrealloc(vals, (size_t)cap * sizeof *vals);
                }
                keys[cnt] = k;
                vals[cnt] = v;
                cnt++;
            } while (p_match(p, TK_COMMA));
        }
        p_expect(p, TK_RBRACE, "}");
        n->u.obj.keys = keys;
        n->u.obj.vals = vals;
        n->u.obj.n    = cnt;
        return n;
    }
    case TK_FN: {
        /* Anonymous function: 'fn' '(' params ')' block  OR  'fn' '(' params ')' '=>' expr */
        p_advance(p);
        p_expect(p, TK_LPAREN, "(");
        Node **params = NULL; int np = 0, pcap = 0;
        if (!p_check(p, TK_RPAREN)) {
            do {
                if (p->cur.kind != TK_IDENT) db_error("parse: expected parameter name at line %d", p->cur.line);
                Node *pn = new_node(N_IDENT, p->cur.line);
                pn->u.ident.name = p->cur.text;
                push_node(&params, &np, &pcap, pn);
                p_advance(p);
            } while (p_match(p, TK_COMMA));
        }
        p_expect(p, TK_RPAREN, ")");
        Node *lam = new_node(N_LAMBDA, t.line);
        lam->u.fn.params = params;
        lam->u.fn.nparams = np;
        if (p_match(p, TK_ARROW)) {
            if (p->cur.kind == TK_LBRACE) lam->u.fn.body = parse_block(p);
            else {
                Node *blk = new_node(N_BLOCK, p->cur.line);
                Node **stmts = NULL; int sn = 0, scap = 0;
                Node *ret = new_node(N_RETURN, p->cur.line);
                ret->u.ret.val = parse_expr(p);
                push_node(&stmts, &sn, &scap, ret);
                blk->u.block.stmts = stmts;
                blk->u.block.n = sn;
                lam->u.fn.body = blk;
            }
        } else {
            lam->u.fn.body = parse_block(p);
        }
        return lam;
    }
    case TK_MINUS: {
        p_advance(p);
        Node *a = parse_primary(p);
        /* Special case: unary minus of literal 0 produces -0. */
        if (a->kind == N_LIT_NUM) { a->u.num = -a->u.num; return a; }
        Node *n = new_node(N_UNARY, t.line);
        n->u.un.op = UN_NEG;
        n->u.un.a  = a;
        return n;
    }
    default:
        db_error("parse: unexpected token %s at line %d", tok_name(t.kind), t.line);
    }
    return NULL;
}

static Node *parse_postfix(Par *p, Node *left) {
    for (;;) {
        Tok t = p->cur;
        if (t.kind == TK_LPAREN) {
            p_advance(p);
            Node **args = NULL; int n = 0, cap = 0;
            if (!p_check(p, TK_RPAREN)) {
                do { push_node(&args, &n, &cap, parse_expr(p)); } while (p_match(p, TK_COMMA));
            }
            p_expect(p, TK_RPAREN, ")");
            Node *c = new_node(N_CALL, t.line);
            c->u.call.callee = left;
            c->u.call.args   = args;
            c->u.call.nargs  = n;
            left = c;
        } else if (t.kind == TK_LBRACKET) {
            p_advance(p);
            Node *idx = parse_expr(p);
            p_expect(p, TK_RBRACKET, "]");
            Node *c = new_node(N_INDEX, t.line);
            c->u.pair.a = left;
            c->u.pair.b = idx;
            left = c;
        } else if (t.kind == TK_DOT) {
            p_advance(p);
            if (p->cur.kind != TK_IDENT) db_error("parse: expected member name at line %d", p->cur.line);
            Node *c = new_node(N_MEMBER, t.line);
            c->u.member.target = left;
            c->u.member.name   = p->cur.text;
            p_advance(p);
            left = c;
        } else break;
    }
    return left;
}

static Node *parse_unary(Par *p) {
    Tok t = p->cur;
    if (t.kind == TK_MINUS) {
        p_advance(p);
        Node *a = parse_unary(p);
        if (a->kind == N_LIT_NUM) { a->u.num = -a->u.num; return a; }
        Node *n = new_node(N_UNARY, t.line);
        n->u.un.op = UN_NEG;
        n->u.un.a  = a;
        return n;
    }
    Node *e = parse_primary(p);
    return parse_postfix(p, e);
}

static int prec(TokKind k) {
    switch (k) {
    case TK_OR: return 1;
    case TK_AND: return 2;
    case TK_EQ2: case TK_EQ3: case TK_EQ4: case TK_EQ5: return 3;
    case TK_LT: case TK_GT: case TK_LE: case TK_GE: return 4;
    case TK_PLUS: case TK_MINUS: return 5;
    case TK_STAR: case TK_SLASH: case TK_PERCENT: return 6;
    default: return -1;
    }
}

static BinOp op_of(TokKind k) {
    switch (k) {
    case TK_PLUS: return OP_ADD;
    case TK_MINUS: return OP_SUB;
    case TK_STAR: return OP_MUL;
    case TK_SLASH: return OP_DIV;
    case TK_PERCENT: return OP_MOD;
    case TK_LT: return OP_LT;
    case TK_GT: return OP_GT;
    case TK_LE: return OP_LE;
    case TK_GE: return OP_GE;
    case TK_AND: return OP_AND;
    case TK_OR: return OP_OR;
    case TK_EQ2: return OP_EQ2;
    case TK_EQ3: return OP_EQ3;
    case TK_EQ4: return OP_EQ4;
    case TK_EQ5: return OP_EQ5;
    default: return OP_ADD;
    }
}

static Node *parse_binop(Par *p, int min_prec) {
    Node *left = parse_unary(p);
    for (;;) {
        int pr = prec(p->cur.kind);
        if (pr < min_prec) break;
        Tok t = p->cur;
        p_advance(p);
        Node *right = parse_binop(p, pr + 1);
        Node *n = new_node(N_BINOP, t.line);
        n->u.bin.op = op_of(t.kind);
        n->u.bin.a  = left;
        n->u.bin.b  = right;
        left = n;
    }
    return left;
}

/* Wrap an LHS expression and an RHS into the appropriate assignment node. */
static Node *make_assign(Node *lhs, Node *rhs, int line) {
    if (lhs->kind == N_IDENT) {
        Node *a = new_node(N_ASSIGN, line);
        a->u.assign.name = lhs->u.ident.name;
        a->u.assign.val  = rhs;
        return a;
    }
    if (lhs->kind == N_INDEX) {
        Node *a = new_node(N_INDEX_SET, line);
        a->u.idxset.target = lhs->u.pair.a;
        a->u.idxset.index  = lhs->u.pair.b;
        a->u.idxset.val    = rhs;
        return a;
    }
    if (lhs->kind == N_MEMBER) {
        Node *a = new_node(N_MEMBER_SET, line);
        a->u.memset_.target = lhs->u.member.target;
        a->u.memset_.member = lhs->u.member.name;
        a->u.memset_.val    = rhs;
        return a;
    }
    db_error("parse: invalid assignment target at line %d", line);
    return NULL;
}

static Node *parse_expr(Par *p) {
    Node *lhs = parse_binop(p, 1);
    /* Right-associative assignment as a low-precedence expression operator,
     * so things like `(e) => keys[e.key] = true` and `f(x = 3)` parse. */
    if (p->cur.kind == TK_ASSIGN) {
        Tok t = p->cur;
        p_advance(p);
        Node *rhs = parse_expr(p);
        return make_assign(lhs, rhs, t.line);
    }
    return lhs;
}

/* Parse a block '{' stmt* '}'. */
static Node *parse_block(Par *p) {
    Tok t = p->cur;
    p_expect(p, TK_LBRACE, "{");
    Node *blk = new_node(N_BLOCK, t.line);
    Node **stmts = NULL; int n = 0, cap = 0;
    while (!p_check(p, TK_RBRACE) && !p_check(p, TK_EOF)) {
        push_node(&stmts, &n, &cap, parse_stmt(p));
    }
    p_expect(p, TK_RBRACE, "}");
    blk->u.block.stmts = stmts;
    blk->u.block.n     = n;
    return blk;
}

/* Parse 'if (cond) blockOrStmt [else blockOrStmt]' */
static Node *parse_if(Par *p) {
    Tok t = p->cur;
    p_advance(p); /* if */
    p_expect(p, TK_LPAREN, "(");
    Node *cond = parse_expr(p);
    p_expect(p, TK_RPAREN, ")");
    Node *then_ = p_check(p, TK_LBRACE) ? parse_block(p) : parse_stmt(p);
    Node *els_  = NULL;
    if (p_match(p, TK_ELSE)) {
        if (p_check(p, TK_IF)) els_ = parse_if(p);
        else els_ = p_check(p, TK_LBRACE) ? parse_block(p) : parse_stmt(p);
    }
    Node *n = new_node(N_IF, t.line);
    n->u.ifs.cond = cond;
    n->u.ifs.then = then_;
    n->u.ifs.els  = els_;
    return n;
}

static Node *parse_while(Par *p) {
    Tok t = p->cur;
    p_advance(p);
    p_expect(p, TK_LPAREN, "(");
    Node *cond = parse_expr(p);
    p_expect(p, TK_RPAREN, ")");
    Node *body = p_check(p, TK_LBRACE) ? parse_block(p) : parse_stmt(p);
    Node *n = new_node(N_WHILE, t.line);
    n->u.whl.cond = cond;
    n->u.whl.body = body;
    return n;
}

static Node *parse_when(Par *p) {
    Tok t = p->cur;
    p_advance(p);
    p_expect(p, TK_LPAREN, "(");
    Node *cond = parse_expr(p);
    p_expect(p, TK_RPAREN, ")");
    Node *body;
    if (p_match(p, TK_ARROW)) {
        if (p->cur.kind == TK_LBRACE) body = parse_block(p);
        else body = parse_stmt(p);
    } else {
        body = p_check(p, TK_LBRACE) ? parse_block(p) : parse_stmt(p);
    }
    Node *n = new_node(N_WHEN, t.line);
    n->u.when.cond = cond;
    n->u.when.body = body;
    return n;
}

/* Consume the trailing !/? terminator if present, returning bangs/debug counts. */
static void maybe_term(Par *p, int *bangs, int *debug) {
    *bangs = 0; *debug = 0;
    if (p->cur.kind == TK_BANG) {
        *bangs = p->cur.ival;
        *debug = p->cur.debug;
        p_advance(p);
    }
}

/* Parse declaration: const|var const|var IDENT = expr ! */
static Node *parse_decl(Par *p) {
    Tok t = p->cur;
    int first_const = p_match(p, TK_CONST);
    int first_var   = !first_const && p_match(p, TK_VAR);
    if (!first_const && !first_var) db_error("parse: expected const/var at line %d", t.line);
    int second_const = p_match(p, TK_CONST);
    int second_var   = !second_const && p_match(p, TK_VAR);
    if (!second_const && !second_var)
        db_error("parse: Dreamberd declarations need two words (const/var const/var) at line %d", t.line);
    DeclKind dk;
    if (first_const && second_const) dk = DK_CC;
    else if (first_const && second_var) dk = DK_CV;
    else if (first_var && second_const) dk = DK_VC;
    else dk = DK_VV;

    if (p->cur.kind != TK_IDENT) db_error("parse: expected identifier after declaration at line %d", p->cur.line);
    char *name = p->cur.text;
    p_advance(p);

    /* Optional TypeScript-style type annotation: `name: SomeType<...>`.
     * The contents may be arbitrary (regex literals, etc.) so we skip
     * them at the source-byte level and just discard. */
    if (p->cur.kind == TK_COLON) {
        p_advance(p);
        /* Drop any token lookahead; lex_skip_to_assign manipulates source. */
        p->have_la = 0;
        if (!lex_skip_to_assign(&p->L)) {
            /* No '=' found; just take the next real token (will likely be EOF). */
        }
        p_advance(p);
    }

    /* Optional lifetime: '<' N | Ns | Infinity | -Infinity '>'. */
    Lifetime lt = { .kind = LT_INF, .n = 0 };
    if (p_match(p, TK_LT)) {
        int neg = p_match(p, TK_MINUS);
        if (p->cur.kind == TK_NUM) {
            double v = p->cur.num;
            /* Check whether the source token text ended in 's' (seconds). */
            int seconds = (p->cur.len > 0 && p->cur.start &&
                           (p->cur.start[p->cur.len - 1] == 's' ||
                            p->cur.start[p->cur.len - 1] == 'S'));
            /* Number lexer doesn't consume trailing 's', so check the
             * next token instead. */
            p_advance(p);
            if (!seconds && p->cur.kind == TK_IDENT &&
                (strcmp(p->cur.text, "s") == 0 || strcmp(p->cur.text, "S") == 0)) {
                seconds = 1;
                p_advance(p);
            }
            lt.kind = seconds ? LT_SECONDS : LT_LINES;
            lt.n    = neg ? -v : v;
            if (lt.n <= 0) lt.kind = LT_DEAD;
        } else if (p->cur.kind == TK_IDENT && strcmp(p->cur.text, "Infinity") == 0) {
            p_advance(p);
            lt.kind = neg ? LT_DEAD : LT_INF;
        } else {
            db_error("parse: expected lifetime (number, 'Ns', or 'Infinity') at line %d", p->cur.line);
        }
        p_expect(p, TK_GT, "> to close lifetime");
    }

    Node *init = NULL;
    if (p_match(p, TK_ASSIGN)) init = parse_expr(p);

    Node *n = new_node(N_DECL, t.line);
    n->u.decl.dk   = dk;
    n->u.decl.name = name;
    n->u.decl.init = init;
    n->u.decl.lt   = lt;
    return n;
}

/* Parse 'function NAME(params) block' or 'fn NAME(params) => expr' */
static Node *parse_fn_decl(Par *p) {
    Tok t = p->cur;
    p_advance(p); /* fn keyword */
    if (p->cur.kind != TK_IDENT) db_error("parse: expected function name at line %d", p->cur.line);
    char *name = p->cur.text;
    p_advance(p);
    p_expect(p, TK_LPAREN, "(");
    Node **params = NULL; int np = 0, pcap = 0;
    if (!p_check(p, TK_RPAREN)) {
        do {
            if (p->cur.kind != TK_IDENT) db_error("parse: expected parameter at line %d", p->cur.line);
            Node *pn = new_node(N_IDENT, p->cur.line);
            pn->u.ident.name = p->cur.text;
            push_node(&params, &np, &pcap, pn);
            p_advance(p);
        } while (p_match(p, TK_COMMA));
    }
    p_expect(p, TK_RPAREN, ")");
    Node *body;
    if (p_match(p, TK_ARROW)) {
        if (p->cur.kind == TK_LBRACE) body = parse_block(p);
        else {
            Node *blk = new_node(N_BLOCK, p->cur.line);
            Node **stmts = NULL; int sn = 0, scap = 0;
            Node *ret = new_node(N_RETURN, p->cur.line);
            ret->u.ret.val = parse_expr(p);
            push_node(&stmts, &sn, &scap, ret);
            blk->u.block.stmts = stmts;
            blk->u.block.n = sn;
            body = blk;
        }
    } else {
        body = parse_block(p);
    }
    Node *n = new_node(N_FN_DECL, t.line);
    n->u.fndecl.name    = name;
    n->u.fndecl.params  = params;
    n->u.fndecl.nparams = np;
    n->u.fndecl.body    = body;
    return n;
}

static Node *parse_class(Par *p) {
    Tok t = p->cur;
    p_advance(p);
    if (p->cur.kind != TK_IDENT) db_error("parse: expected class name at line %d", p->cur.line);
    char *name = p->cur.text;
    p_advance(p);
    Node *body = parse_block(p);
    Node *n = new_node(N_CLASS_DECL, t.line);
    n->u.cls.name = name;
    n->u.cls.body = body;
    n->u.cls.instance_cap = 2;
    return n;
}

/* Wrap a "logical statement" with its bang/debug terminator. */
static Node *wrap_stmt(Node *inner, int bangs, int debug) {
    Node *n = new_node(N_STMT, inner->line);
    n->u.stmt.inner = inner;
    n->u.stmt.bangs = bangs;
    n->u.stmt.debug = debug;
    return n;
}

/* Statement-level entry that accepts assignment or general expression. */
static Node *parse_assign_or_expr(Par *p) {
    return parse_expr(p);
}

static Node *parse_stmt(Par *p) {
    Tok t = p->cur;
    int bangs = 0, debug = 0;

    if (t.kind == TK_CONST || t.kind == TK_VAR) {
        Node *d = parse_decl(p);
        maybe_term(p, &bangs, &debug);
        return wrap_stmt(d, bangs, debug);
    }
    if (t.kind == TK_FN) {
        /* Distinguish anon 'fn (...)' used as expression vs named decl 'fn name(...)'. */
        Tok la = p_peek(p);
        if (la.kind == TK_IDENT) {
            Node *fd = parse_fn_decl(p);
            maybe_term(p, &bangs, &debug);
            return wrap_stmt(fd, bangs, debug);
        }
        /* else fall through to expression */
    }
    if (t.kind == TK_CLASS) {
        Node *c = parse_class(p);
        maybe_term(p, &bangs, &debug);
        return wrap_stmt(c, bangs, debug);
    }
    if (t.kind == TK_IF) {
        Node *n = parse_if(p);
        maybe_term(p, &bangs, &debug);
        return wrap_stmt(n, bangs, debug);
    }
    if (t.kind == TK_WHILE) {
        Node *n = parse_while(p);
        maybe_term(p, &bangs, &debug);
        return wrap_stmt(n, bangs, debug);
    }
    if (t.kind == TK_WHEN) {
        Node *n = parse_when(p);
        maybe_term(p, &bangs, &debug);
        return wrap_stmt(n, bangs, debug);
    }
    if (t.kind == TK_RETURN) {
        p_advance(p);
        Node *ret = new_node(N_RETURN, t.line);
        if (!p_check(p, TK_BANG) && !p_check(p, TK_RBRACE) && !p_check(p, TK_EOF))
            ret->u.ret.val = parse_expr(p);
        maybe_term(p, &bangs, &debug);
        return wrap_stmt(ret, bangs, debug);
    }
    if (t.kind == TK_DELETE) {
        p_advance(p);
        Node *target = parse_expr(p);
        Node *n = new_node(N_DELETE, t.line);
        n->u.del.target = target;
        maybe_term(p, &bangs, &debug);
        return wrap_stmt(n, bangs, debug);
    }
    if (t.kind == TK_LBRACE) {
        /* bare block */
        Node *b = parse_block(p);
        maybe_term(p, &bangs, &debug);
        return wrap_stmt(b, bangs, debug);
    }
    /* Expression / assignment statement */
    Node *e = parse_assign_or_expr(p);
    maybe_term(p, &bangs, &debug);
    return wrap_stmt(e, bangs, debug);
}

Node *parse_program(const char *src, size_t len) {
    Par p = {0};
    lex_init(&p.L, src, len);
    p_advance(&p);
    Node *prog = new_node(N_PROGRAM, 1);
    Node **stmts = NULL; int n = 0, cap = 0;
    while (!p_check(&p, TK_EOF)) {
        push_node(&stmts, &n, &cap, parse_stmt(&p));
    }
    prog->u.block.stmts = stmts;
    prog->u.block.n     = n;
    return prog;
}

const char *binop_name(BinOp op) {
    switch (op) {
    case OP_ADD: return "+";
    case OP_SUB: return "-";
    case OP_MUL: return "*";
    case OP_DIV: return "/";
    case OP_MOD: return "%";
    case OP_LT:  return "<";
    case OP_GT:  return ">";
    case OP_LE:  return "<=";
    case OP_GE:  return ">=";
    case OP_AND: return "&&";
    case OP_OR:  return "||";
    case OP_EQ2: return "==";
    case OP_EQ3: return "===";
    case OP_EQ4: return "====";
    case OP_EQ5: return "=====";
    }
    return "?";
}
