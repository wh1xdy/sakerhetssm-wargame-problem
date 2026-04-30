#include "lexer.h"

#include <ctype.h>

static int peek(Lexer *L, int off) {
    size_t p = L->pos + (size_t)off;
    if (p >= L->srclen) return -1;
    return (unsigned char)L->src[p];
}

static int advance(Lexer *L) {
    if (L->pos >= L->srclen) return -1;
    int c = (unsigned char)L->src[L->pos++];
    if (c == '\n') L->line++;
    return c;
}

static Tok mktok(Lexer *L, TokKind k) {
    Tok t = {0};
    t.kind = k;
    t.line = L->line;
    return t;
}

static void skip_ws_and_comments(Lexer *L) {
    for (;;) {
        int c = peek(L, 0);
        if (c == -1) return;
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') { advance(L); continue; }
        if (c == '/' && peek(L, 1) == '/') {
            while (peek(L, 0) != -1 && peek(L, 0) != '\n') advance(L);
            continue;
        }
        return;
    }
}

/* Check whether word is a non-empty subsequence of "function" (case-insensitive).
 * Must start with 'f'. Accepts: f, fn, fu, fun, func, funct, functi, functio,
 * function, fucn-of-course-not (no, order must be preserved). */
static int is_fn_prefix(const char *s, size_t n) {
    static const char target[] = "function";
    if (n == 0 || n > 8) return 0;
    size_t ti = 0;
    for (size_t i = 0; i < n; i++) {
        char a = s[i];
        if (a >= 'A' && a <= 'Z') a = a - 'A' + 'a';
        while (ti < 8 && target[ti] != a) ti++;
        if (ti == 8) return 0;
        ti++;
    }
    /* require that first char is 'f' so random words starting elsewhere don't match. */
    char first = s[0];
    if (first >= 'A' && first <= 'Z') first = first - 'A' + 'a';
    return first == 'f';
}

static TokKind keyword_of(const char *s, size_t n) {
    #define KW(str, k) if (n == sizeof(str)-1 && memcmp(s, str, n) == 0) return k
    KW("const", TK_CONST);
    KW("var", TK_VAR);
    KW("if", TK_IF);
    KW("else", TK_ELSE);
    KW("while", TK_WHILE);
    KW("return", TK_RETURN);
    KW("true", TK_TRUE);
    KW("false", TK_FALSE);
    KW("maybe", TK_MAYBE);
    KW("undefined", TK_UNDEFINED);
    KW("previous", TK_PREVIOUS);
    KW("next", TK_NEXT);
    KW("when", TK_WHEN);
    KW("class", TK_CLASS);
    KW("new", TK_NEW);
    KW("delete", TK_DELETE);
    #undef KW
    if (is_fn_prefix(s, n)) return TK_FN;
    return TK_IDENT;
}

static Tok read_number(Lexer *L) {
    size_t start = L->pos;
    int saw_dot = 0;
    while (peek(L, 0) != -1 && (isdigit(peek(L, 0)) || (!saw_dot && peek(L, 0) == '.' && isdigit(peek(L, 1))))) {
        if (peek(L, 0) == '.') saw_dot = 1;
        advance(L);
    }
    Tok t = mktok(L, TK_NUM);
    t.start = L->src + start;
    t.len   = L->pos - start;
    char *tmp = xstrndup(t.start, t.len);
    t.num = strtod(tmp, NULL);
    free(tmp);
    return t;
}

static Tok read_ident(Lexer *L) {
    size_t start = L->pos;
    while (peek(L, 0) != -1 && (isalnum(peek(L, 0)) || peek(L, 0) == '_')) advance(L);
    Tok t = mktok(L, TK_IDENT);
    t.start = L->src + start;
    t.len   = L->pos - start;
    t.text  = xstrndup(t.start, t.len);
    t.kind  = keyword_of(t.start, t.len);
    return t;
}

/* Read a string that uses N identical quote chars at the open.
 * Supports escape sequences and `${...}` interpolation.
 * Returns a single TK_STR token if no interpolation, otherwise emits
 * a TK_STR_CHUNK followed by queued TK_INTERP_START; further chunks/interp
 * parts are produced as the parser consumes the lexer. */
static Tok read_string_start(Lexer *L) {
    int qc = peek(L, 0);
    int run = 0;
    while (peek(L, 0) == qc) { advance(L); run++; }
    /* Disambiguation: if the opener is exactly 2 quotes AND the next
     * character looks like the end of an expression (so there's no body
     * to read), treat it as an empty single-quote string instead of a
     * 2-quote opener. This lets `print("")` work while preserving
     * `""multi quote""` strings. */
    if (run == 2) {
        int nx = peek(L, 0);
        if (nx == -1 || nx == ')' || nx == ']' || nx == '}' || nx == ','
            || nx == '!' || nx == '?' || nx == ';' || nx == ':'
            || nx == ' ' || nx == '\t' || nx == '\n' || nx == '\r') {
            Tok t = mktok(L, TK_STR);
            t.text = xstrdup("");
            t.len  = 0;
            return t;
        }
    }
    /* read body until matching run of qc, handling \ escapes and ${ */
    Buf body; buf_init(&body);
    int interpolated = 0;
    Tok first_chunk = mktok(L, TK_STR);
    for (;;) {
        int c = peek(L, 0);
        /* AQMI: Automatic-Quotation-Marks-Insertion. If the source ends
         * before the string is closed, just close it here. */
        if (c == -1) break;
        /* check run of closing quotes */
        if (c == qc) {
            int matched = 1;
            for (int i = 0; i < run; i++) {
                if (peek(L, i) != qc) { matched = 0; break; }
            }
            if (matched) {
                for (int i = 0; i < run; i++) advance(L);
                break;
            }
        }
        if (c == '\\') {
            advance(L);
            int e = advance(L);
            switch (e) {
            case 'n': buf_push(&body, '\n'); break;
            case 't': buf_push(&body, '\t'); break;
            case 'r': buf_push(&body, '\r'); break;
            case '\\': buf_push(&body, '\\'); break;
            case '"': buf_push(&body, '"'); break;
            case '\'': buf_push(&body, '\''); break;
            case '`': buf_push(&body, '`'); break;
            case '$': buf_push(&body, '$'); break;
            case '0': buf_push(&body, '\0'); break;
            default:
                if (e != -1) buf_push(&body, (char)e);
            }
            continue;
        }
        if (c == '$' && peek(L, 1) == '{') {
            /* Start interpolation */
            if (L->depth >= (int)(sizeof L->quote_chars / sizeof L->quote_chars[0]))
                db_error("string interpolation too deeply nested");
            advance(L); advance(L); /* consume ${ */
            L->quote_chars[L->depth] = qc;
            L->quote_runs[L->depth]  = run;
            L->braces_open[L->depth] = 0;
            L->depth++;
            interpolated = 1;
            first_chunk.kind = TK_STR_CHUNK;
            first_chunk.text = body.data ? body.data : xstrdup("");
            first_chunk.len  = body.len;
            /* Queue TK_INTERP_START to be returned next */
            Tok s = mktok(L, TK_INTERP_START);
            int next = (L->qtail + 1) % (int)(sizeof L->queued / sizeof L->queued[0]);
            L->queued[L->qtail] = s;
            L->qtail = next;
            return first_chunk;
        }
        advance(L);
        buf_push(&body, (char)c);
    }
    /* Closed the string */
    if (!interpolated) {
        Tok t = mktok(L, TK_STR);
        t.text = body.data ? body.data : xstrdup("");
        t.len  = body.len;
        return t;
    }
    /* Shouldn't reach: if we'd started interpolation we'd have returned the chunk. */
    Tok t = mktok(L, TK_STR_CHUNK);
    t.text = body.data ? body.data : xstrdup("");
    t.len  = body.len;
    return t;
}

/* Called when inside an interpolation and we hit a non-brace `}` that
 * closes the interp at the current depth. Resumes the surrounding string. */
static Tok resume_string(Lexer *L) {
    int qc  = L->quote_chars[L->depth - 1];
    int run = L->quote_runs[L->depth - 1];
    L->depth--;
    Buf body; buf_init(&body);
    int interpolated = 0;
    for (;;) {
        int c = peek(L, 0);
        /* AQMI on resume too. */
        if (c == -1) break;
        if (c == qc) {
            int matched = 1;
            for (int i = 0; i < run; i++) {
                if (peek(L, i) != qc) { matched = 0; break; }
            }
            if (matched) { for (int i = 0; i < run; i++) advance(L); break; }
        }
        if (c == '\\') {
            advance(L);
            int e = advance(L);
            switch (e) {
            case 'n': buf_push(&body, '\n'); break;
            case 't': buf_push(&body, '\t'); break;
            case 'r': buf_push(&body, '\r'); break;
            case '\\': buf_push(&body, '\\'); break;
            case '"': buf_push(&body, '"'); break;
            case '\'': buf_push(&body, '\''); break;
            case '`': buf_push(&body, '`'); break;
            case '$': buf_push(&body, '$'); break;
            default: if (e != -1) buf_push(&body, (char)e);
            }
            continue;
        }
        if (c == '$' && peek(L, 1) == '{') {
            advance(L); advance(L);
            L->quote_chars[L->depth] = qc;
            L->quote_runs[L->depth]  = run;
            L->braces_open[L->depth] = 0;
            L->depth++;
            interpolated = 1;
            Tok chunk = mktok(L, TK_STR_CHUNK);
            chunk.text = body.data ? body.data : xstrdup("");
            chunk.len  = body.len;
            Tok s = mktok(L, TK_INTERP_START);
            int next = (L->qtail + 1) % (int)(sizeof L->queued / sizeof L->queued[0]);
            L->queued[L->qtail] = s;
            L->qtail = next;
            return chunk;
        }
        advance(L);
        buf_push(&body, (char)c);
    }
    (void)interpolated;
    Tok t = mktok(L, TK_STR_CHUNK);
    t.text = body.data ? body.data : xstrdup("");
    t.len  = body.len;
    /* This is the final chunk: the parser uses the absence of a following
     * INTERP_START to know the template ended. We flag that by queuing nothing. */
    return t;
}

void lex_init(Lexer *L, const char *src, size_t len) {
    memset(L, 0, sizeof *L);
    L->src    = src;
    L->srclen = len;
    L->pos    = 0;
    L->line   = 1;
}

static Tok read_bang(Lexer *L) {
    int bangs = 0, qs = 0;
    while (peek(L, 0) == '!' || peek(L, 0) == '?') {
        int c = advance(L);
        if (c == '!') bangs++; else qs++;
    }
    Tok t = mktok(L, TK_BANG);
    t.ival  = bangs;
    t.debug = qs;
    return t;
}

Tok lex_next(Lexer *L) {
    /* Drain queued tokens. */
    if (L->qhead != L->qtail) {
        Tok t = L->queued[L->qhead];
        L->qhead = (L->qhead + 1) % (int)(sizeof L->queued / sizeof L->queued[0]);
        return t;
    }

    skip_ws_and_comments(L);
    int c = peek(L, 0);
    if (c == -1) return mktok(L, TK_EOF);

    if (isdigit(c)) return read_number(L);
    if (isalpha(c) || c == '_') return read_ident(L);

    if (c == '"' || c == '\'') return read_string_start(L);

    /* Inside an interpolation, closing '}' terminates it if no braces open. */
    if (c == '}' && L->depth > 0 && L->braces_open[L->depth - 1] == 0) {
        advance(L);
        Tok t = mktok(L, TK_INTERP_END);
        /* After INTERP_END, queue the string continuation chunk. */
        Tok chunk = resume_string(L);
        int next = (L->qtail + 1) % (int)(sizeof L->queued / sizeof L->queued[0]);
        L->queued[L->qtail] = chunk;
        L->qtail = next;
        return t;
    }

    if (c == '!' || c == '?') return read_bang(L);

    /* Equality runs */
    if (c == '=') {
        int n = 0;
        while (peek(L, 0) == '=') { advance(L); n++; }
        /* Handle '=>' (only when n == 1 and '>' follows) */
        if (n == 1 && peek(L, 0) == '>') { advance(L); return mktok(L, TK_ARROW); }
        switch (n) {
        case 1: return mktok(L, TK_ASSIGN);
        case 2: return mktok(L, TK_EQ2);
        case 3: return mktok(L, TK_EQ3);
        case 4: return mktok(L, TK_EQ4);
        default: return mktok(L, TK_EQ5);
        }
    }

    advance(L);
    switch (c) {
    case '(': return mktok(L, TK_LPAREN);
    case ')': return mktok(L, TK_RPAREN);
    case '{':
        if (L->depth > 0) L->braces_open[L->depth - 1]++;
        return mktok(L, TK_LBRACE);
    case '}':
        if (L->depth > 0 && L->braces_open[L->depth - 1] > 0) L->braces_open[L->depth - 1]--;
        return mktok(L, TK_RBRACE);
    case '[': return mktok(L, TK_LBRACKET);
    case ']': return mktok(L, TK_RBRACKET);
    case ',': return mktok(L, TK_COMMA);
    case '.': return mktok(L, TK_DOT);
    case ':': return mktok(L, TK_COLON);
    case '+': return mktok(L, TK_PLUS);
    case '-': return mktok(L, TK_MINUS);
    case '*': return mktok(L, TK_STAR);
    case '/': return mktok(L, TK_SLASH);
    case '%': return mktok(L, TK_PERCENT);
    case '<':
        if (peek(L, 0) == '=') { advance(L); return mktok(L, TK_LE); }
        return mktok(L, TK_LT);
    case '>':
        if (peek(L, 0) == '=') { advance(L); return mktok(L, TK_GE); }
        return mktok(L, TK_GT);
    case '&':
        if (peek(L, 0) == '&') { advance(L); return mktok(L, TK_AND); }
        return mktok(L, TK_AND); /* single & also AND */
    case '|':
        if (peek(L, 0) == '|') { advance(L); return mktok(L, TK_OR); }
        return mktok(L, TK_OR);
    }
    db_error("unexpected character '%c' at line %d", c, L->line);
    return mktok(L, TK_EOF); /* unreachable */
}

int lex_skip_to_assign(Lexer *L) {
    int angle = 0;
    while (L->pos < L->srclen) {
        char c = L->src[L->pos];
        if (c == '<') { angle++; L->pos++; continue; }
        if (c == '>') { angle--; L->pos++; continue; }
        if (c == '=' && angle <= 0) return 1;
        if (c == '\n') L->line++;
        L->pos++;
    }
    return 0;
}

const char *tok_name(TokKind k) {
    switch (k) {
    case TK_EOF: return "EOF";
    case TK_NUM: return "number";
    case TK_STR: return "string";
    case TK_STR_CHUNK: return "string-chunk";
    case TK_INTERP_START: return "${";
    case TK_INTERP_END: return "}(interp)";
    case TK_IDENT: return "identifier";
    case TK_CONST: return "const";
    case TK_VAR: return "var";
    case TK_IF: return "if";
    case TK_ELSE: return "else";
    case TK_WHILE: return "while";
    case TK_RETURN: return "return";
    case TK_TRUE: return "true";
    case TK_FALSE: return "false";
    case TK_MAYBE: return "maybe";
    case TK_UNDEFINED: return "undefined";
    case TK_PREVIOUS: return "previous";
    case TK_NEXT: return "next";
    case TK_WHEN: return "when";
    case TK_CLASS: return "class";
    case TK_NEW: return "new";
    case TK_DELETE: return "delete";
    case TK_FN: return "function";
    case TK_LPAREN: return "(";
    case TK_RPAREN: return ")";
    case TK_LBRACE: return "{";
    case TK_RBRACE: return "}";
    case TK_LBRACKET: return "[";
    case TK_RBRACKET: return "]";
    case TK_COMMA: return ",";
    case TK_DOT: return ".";
    case TK_COLON: return ":";
    case TK_ARROW: return "=>";
    case TK_PLUS: return "+";
    case TK_MINUS: return "-";
    case TK_STAR: return "*";
    case TK_SLASH: return "/";
    case TK_PERCENT: return "%";
    case TK_LT: return "<";
    case TK_GT: return ">";
    case TK_LE: return "<=";
    case TK_GE: return ">=";
    case TK_AND: return "&&";
    case TK_OR: return "||";
    case TK_NOT: return "!";
    case TK_ASSIGN: return "=";
    case TK_EQ2: return "==";
    case TK_EQ3: return "===";
    case TK_EQ4: return "====";
    case TK_EQ5: return "=====";
    case TK_BANG: return "!";
    }
    return "?";
}
