#include "eval.h"
#include "builtins.h"

#include <math.h>
#include <time.h>

double interp_now(void) {
    struct timespec ts;
#ifdef CLOCK_MONOTONIC
    clock_gettime(CLOCK_MONOTONIC, &ts);
#else
    clock_gettime(CLOCK_REALTIME, &ts);
#endif
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

void interp_register_lifetime(Interp *I, Slot *s) {
    if (I->n_lt_slots + 1 > I->cap_lt_slots) {
        I->cap_lt_slots = I->cap_lt_slots ? I->cap_lt_slots * 2 : 8;
        I->lt_slots = xrealloc(I->lt_slots, (size_t)I->cap_lt_slots * sizeof *I->lt_slots);
    }
    I->lt_slots[I->n_lt_slots++] = s;
}

void interp_sweep_lifetimes(Interp *I) {
    double now = -1.0;
    int w = 0;
    for (int r = 0; r < I->n_lt_slots; r++) {
        Slot *s = I->lt_slots[r];
        if (s->deleted) continue; /* drop from list */
        int expired = 0;
        if (s->lt_kind == LT_LINES) {
            if (I->line_counter >= s->expire_line) expired = 1;
        } else if (s->lt_kind == LT_SECONDS) {
            if (now < 0) now = interp_now();
            if (now >= s->expire_time) expired = 1;
        } else if (s->lt_kind == LT_DEAD) {
            expired = 1;
        }
        if (expired) { s->deleted = 1; continue; }
        I->lt_slots[w++] = s;
    }
    I->n_lt_slots = w;
}

/* ---------- delete helpers ---------- */

int is_num_deleted(Interp *I, double x) {
    for (int i = 0; i < I->n_del_nums; i++)
        if (I->del_nums[i] == x || (I->del_nums[i] != I->del_nums[i] && x != x)) return 1;
    return 0;
}

int is_str_deleted(Interp *I, const char *s, size_t n) {
    for (int i = 0; i < I->n_del_strs; i++) {
        if (strlen(I->del_strs[i]) == n && memcmp(I->del_strs[i], s, n) == 0) return 1;
    }
    return 0;
}

int is_type_deleted(Interp *I, const char *name) {
    for (int i = 0; i < I->n_del_types; i++)
        if (strcmp(I->del_types[i], name) == 0) return 1;
    return 0;
}

static void del_num(Interp *I, double x) {
    if (I->n_del_nums + 1 > I->cap_del_nums) {
        I->cap_del_nums = I->cap_del_nums ? I->cap_del_nums * 2 : 4;
        I->del_nums = xrealloc(I->del_nums, (size_t)I->cap_del_nums * sizeof *I->del_nums);
    }
    I->del_nums[I->n_del_nums++] = x;
}

static void del_str(Interp *I, const char *s, size_t n) {
    if (I->n_del_strs + 1 > I->cap_del_strs) {
        I->cap_del_strs = I->cap_del_strs ? I->cap_del_strs * 2 : 4;
        I->del_strs = xrealloc(I->del_strs, (size_t)I->cap_del_strs * sizeof *I->del_strs);
    }
    I->del_strs[I->n_del_strs++] = xstrndup(s, n);
}

static void del_type(Interp *I, const char *name) {
    if (I->n_del_types + 1 > I->cap_del_types) {
        I->cap_del_types = I->cap_del_types ? I->cap_del_types * 2 : 4;
        I->del_types = xrealloc(I->del_types, (size_t)I->cap_del_types * sizeof *I->del_types);
    }
    I->del_types[I->n_del_types++] = xstrdup(name);
}

/* Release heap storage held by v. Other live references are not updated. */
static void free_value_payload(Value v) {
    switch (v.t) {
    case V_STR:
        if (v.u.s) {
            free(v.u.s->data);
            free(v.u.s);
        }
        break;
    case V_ARR:
        if (v.u.a) {
            free(v.u.a->items);
            free(v.u.a);
        }
        break;
    case V_OBJ:
        if (v.u.o) {
            ObjEntry *e = v.u.o->head;
            while (e) {
                ObjEntry *next = e->next;
                free(e->key);
                free(e->val);
                free(e);
                e = next;
            }
            free(v.u.o);
        }
        break;
    case V_FN:
        if (v.u.f) {
            free(v.u.f->name);
            free(v.u.f);
        }
        break;
    case V_CLASS:
        if (v.u.c) {
            free(v.u.c->name);
            free(v.u.c);
        }
        break;
    case V_INST:
        if (v.u.i) free(v.u.i);
        break;
    case V_BUILTIN:
        if (v.u.bi) slop_recycle_next_alloc(v.u.bi, sizeof *v.u.bi);
        break;
    default:
        break;
    }
}

/* ---------- interpreter ---------- */

Interp *interp_new(void) {
    Interp *I = xcalloc(1, sizeof *I);
    I->globals = env_new(NULL);
    builtins_install(I);
    return I;
}

static void register_watcher(Interp *I, Node *cond, Node *body, Env *env) {
    if (I->nwatchers + 1 > I->cap_watchers) {
        I->cap_watchers = I->cap_watchers ? I->cap_watchers * 2 : 4;
        I->watchers = xrealloc(I->watchers, (size_t)I->cap_watchers * sizeof *I->watchers);
    }
    Watcher *w = xcalloc(1, sizeof *w);
    w->cond = cond;
    w->body = body;
    w->env  = env;
    w->last = B_FALSE;
    I->watchers[I->nwatchers++] = w;
}

/* Check all watchers; if a condition has gone from not-truthy to truthy, fire. */
void run_watchers(Interp *I) {
    /* Prevent infinite recursion by taking a snapshot. */
    int n = I->nwatchers;
    for (int i = 0; i < n; i++) {
        Watcher *w = I->watchers[i];
        Value c = eval_node(I, w->env, w->cond);
        Bool3 now = v_truthy(c);
        int fired = 0;
        if (now == B_TRUE && w->last != B_TRUE) fired = 1;
        if (now == B_MAYBE && w->last != B_MAYBE && v_truthy_det(c)) fired = 1;
        w->last = now;
        if (fired) {
            eval_node(I, w->env, w->body);
            if (I->ret_set) return;
        }
    }
}

/* Helpers for arithmetic coercion. */
static double to_num(Value v) {
    switch (v.t) {
    case V_NUM: return v.u.num;
    case V_BOOL: return v.u.b == B_TRUE ? 1.0 : v.u.b == B_MAYBE ? 0.5 : 0.0;
    case V_STR: {
        char *end = NULL;
        double d = strtod(v.u.s->data, &end);
        if (end == v.u.s->data) return NAN;
        return d;
    }
    case V_UNDEF: return NAN;
    default: return NAN;
    }
}

static Value num_or_die(Interp *I, double x) {
    /* delete N! makes the value N unavailable everywhere, including as
     * the result of arithmetic. */
    if (is_num_deleted(I, x)) db_error("the number %g has been deleted", x);
    return v_num(x);
}

static Value do_binop(Interp *I, BinOp op, Value a, Value b) {
    switch (op) {
    case OP_ADD: {
        if (a.t == V_STR || b.t == V_STR) return v_str_concat(a, b);
        return num_or_die(I, to_num(a) + to_num(b));
    }
    case OP_SUB: return num_or_die(I, to_num(a) - to_num(b));
    case OP_MUL: return num_or_die(I, to_num(a) * to_num(b));
    case OP_DIV: {
        double y = to_num(b);
        return num_or_die(I, to_num(a) / y);
    }
    case OP_MOD: {
        double x = to_num(a), y = to_num(b);
        return num_or_die(I, fmod(x, y));
    }
    case OP_LT: return v_bool(to_num(a) <  to_num(b) ? B_TRUE : B_FALSE);
    case OP_GT: return v_bool(to_num(a) >  to_num(b) ? B_TRUE : B_FALSE);
    case OP_LE: return v_bool(to_num(a) <= to_num(b) ? B_TRUE : B_FALSE);
    case OP_GE: return v_bool(to_num(a) >= to_num(b) ? B_TRUE : B_FALSE);
    case OP_AND: {
        Bool3 ta = v_truthy(a), tb = v_truthy(b);
        if (ta == B_FALSE || tb == B_FALSE) return v_bool(B_FALSE);
        if (ta == B_MAYBE || tb == B_MAYBE) return v_bool(B_MAYBE);
        return v_bool(B_TRUE);
    }
    case OP_OR: {
        Bool3 ta = v_truthy(a), tb = v_truthy(b);
        if (ta == B_TRUE  || tb == B_TRUE)  return v_bool(B_TRUE);
        if (ta == B_MAYBE || tb == B_MAYBE) return v_bool(B_MAYBE);
        return v_bool(B_FALSE);
    }
    case OP_EQ2: {
        Bool3 m;
        int r = v_eq_loose(a, b, &m);
        if (m == B_MAYBE) return v_bool(B_MAYBE);
        return v_bool(r ? B_TRUE : B_FALSE);
    }
    case OP_EQ3: {
        /* Slightly stricter: requires same type family (num/str/bool).
         * If types differ, yields 'maybe'. Otherwise same as loose. */
        if (a.t != b.t && !((a.t == V_NUM && b.t == V_STR) || (a.t == V_STR && b.t == V_NUM)))
            return v_bool(B_MAYBE);
        Bool3 m;
        int r = v_eq_loose(a, b, &m);
        if (m == B_MAYBE) return v_bool(B_MAYBE);
        return v_bool(r ? B_TRUE : B_FALSE);
    }
    case OP_EQ4: return v_bool(v_eq_value(a, b) ? B_TRUE : B_FALSE);
    case OP_EQ5: return v_bool(v_eq_ref(a, b)   ? B_TRUE : B_FALSE);
    }
    return v_undef();
}

/* Evaluate a single AST node. */
Value eval_node(Interp *I, Env *env, Node *n) {
    if (!n) return v_undef();
    switch (n->kind) {
    case N_LIT_NUM: {
        if (is_num_deleted(I, n->u.num))
            db_error("the number %g has been deleted", n->u.num);
        return v_num(n->u.num);
    }
    case N_LIT_STR: {
        if (is_str_deleted(I, n->u.str.data, n->u.str.len))
            db_error("this string has been deleted");
        return v_strn(n->u.str.data, n->u.str.len);
    }
    case N_LIT_BOOL:  return v_bool(n->u.boolv);
    case N_LIT_UNDEF: return v_undef();

    case N_TEMPLATE: {
        Buf buf; buf_init(&buf);
        for (int i = 0; i < n->u.arr.n; i++) {
            Value v = eval_node(I, env, n->u.arr.items[i]);
            if (v.t == V_STR) buf_append(&buf, v.u.s->data, v.u.s->len);
            else {
                char *mem = NULL; size_t sz = 0;
                FILE *f = open_memstream(&mem, &sz);
                if (f) { v_print(f, v); fclose(f); buf_append(&buf, mem, sz); free(mem); }
            }
        }
        if (!buf.data) { buf.data = xmalloc(1); buf.data[0] = 0; }
        return v_str_take(buf.data, buf.len);
    }

    case N_ARRAY: {
        Value v = v_arr();
        for (int i = 0; i < n->u.arr.n; i++)
            arr_push(v.u.a, eval_node(I, env, n->u.arr.items[i]));
        return v;
    }

    case N_OBJECT: {
        Value v = v_obj();
        for (int i = 0; i < n->u.obj.n; i++)
            obj_set(v.u.o, n->u.obj.keys[i], eval_node(I, env, n->u.obj.vals[i]));
        return v;
    }

    case N_IDENT: {
        Slot *s = env_find(env, n->u.ident.name);
        if (!s || s->deleted) db_error("undefined variable '%s'", n->u.ident.name);
        return s->v;
    }

    case N_UNARY: {
        Value a = eval_node(I, env, n->u.un.a);
        if (n->u.un.op == UN_NEG) return v_num(-to_num(a));
        /* UN_NOT */ {
            Bool3 t = v_truthy(a);
            if (t == B_MAYBE) return v_bool(B_MAYBE);
            return v_bool(t == B_TRUE ? B_FALSE : B_TRUE);
        }
    }

    case N_BINOP: {
        BinOp op = n->u.bin.op;
        /* short-circuit logical */
        if (op == OP_AND) {
            Value a = eval_node(I, env, n->u.bin.a);
            Bool3 ta = v_truthy(a);
            if (ta == B_FALSE) return v_bool(B_FALSE);
            Value b = eval_node(I, env, n->u.bin.b);
            Bool3 tb = v_truthy(b);
            if (tb == B_FALSE) return v_bool(B_FALSE);
            if (ta == B_MAYBE || tb == B_MAYBE) return v_bool(B_MAYBE);
            return v_bool(B_TRUE);
        }
        if (op == OP_OR) {
            Value a = eval_node(I, env, n->u.bin.a);
            Bool3 ta = v_truthy(a);
            if (ta == B_TRUE) return v_bool(B_TRUE);
            Value b = eval_node(I, env, n->u.bin.b);
            Bool3 tb = v_truthy(b);
            if (tb == B_TRUE) return v_bool(B_TRUE);
            if (ta == B_MAYBE || tb == B_MAYBE) return v_bool(B_MAYBE);
            return v_bool(B_FALSE);
        }
        Value a = eval_node(I, env, n->u.bin.a);
        Value b = eval_node(I, env, n->u.bin.b);
        return do_binop(I, op, a, b);
    }

    case N_INDEX: {
        Value target = eval_node(I, env, n->u.pair.a);
        Value idx    = eval_node(I, env, n->u.pair.b);
        if (target.t == V_ARR) {
            /* Dreamberd arrays start at -1: element k is stored at internal k+1. */
            if (idx.t != V_NUM) db_error("array index must be a number");
            long i = (long)idx.u.num + 1;
            if (i < 0 || (size_t)i >= target.u.a->len) return v_undef();
            return target.u.a->items[i];
        }
        if (target.t == V_OBJ) {
            if (idx.t != V_STR) db_error("object index must be a string");
            Value *p = obj_get(target.u.o, idx.u.s->data);
            return p ? *p : v_undef();
        }
        if (target.t == V_STR) {
            if (idx.t != V_NUM) db_error("string index must be a number");
            long i = (long)idx.u.num + 1;
            if (i < 0 || (size_t)i >= target.u.s->len) return v_undef();
            return v_strn(target.u.s->data + i, 1);
        }
        if (target.t == V_INST) {
            if (idx.t != V_STR) db_error("instance index must be a string");
            Slot *s = env_find_local(target.u.i->fields, idx.u.s->data);
            return s ? s->v : v_undef();
        }
        db_error("cannot index into %s", v_typename(target));
    }

    case N_MEMBER: {
        Value target = eval_node(I, env, n->u.member.target);
        const char *name = n->u.member.name;
        if (target.t == V_OBJ) {
            Value *p = obj_get(target.u.o, name);
            return p ? *p : v_undef();
        }
        if (target.t == V_INST) {
            Slot *s = env_find_local(target.u.i->fields, name);
            if (s) return s->v;
            return v_undef();
        }
        if (target.t == V_ARR) {
            if (strcmp(name, "length") == 0) return v_num((double)target.u.a->len);
        }
        if (target.t == V_STR) {
            if (strcmp(name, "length") == 0) return v_num((double)target.u.s->len);
        }
        db_error("cannot read member '%s' from %s", name, v_typename(target));
    }

    case N_CALL: {
        /* Bind self if this is a method call on an instance. */
        Value self_val = v_undef();
        int have_self = 0;
        Value callee;
        if (n->u.call.callee->kind == N_MEMBER) {
            Value target = eval_node(I, env, n->u.call.callee->u.member.target);
            const char *name = n->u.call.callee->u.member.name;
            if (target.t == V_INST) {
                Slot *s = env_find_local(target.u.i->fields, name);
                if (!s) db_error("no method '%s' on instance", name);
                callee = s->v;
                self_val = target; have_self = 1;
            } else if (target.t == V_OBJ) {
                Value *p = obj_get(target.u.o, name);
                if (!p) db_error("no member '%s' on object", name);
                callee = *p;
                self_val = target; have_self = 1;
            } else {
                /* fall back: re-evaluate normally */
                callee = eval_node(I, env, n->u.call.callee);
            }
        } else {
            callee = eval_node(I, env, n->u.call.callee);
        }
        int nargs = n->u.call.nargs;
        Value *args = nargs ? xmalloc((size_t)nargs * sizeof *args) : NULL;
        for (int i = 0; i < nargs; i++) args[i] = eval_node(I, env, n->u.call.args[i]);
        Value result = v_undef();
        if (callee.t == V_BUILTIN) {
            result = callee.u.bi->fn(I, args, nargs);
        } else if (callee.t == V_FN) {
            Fn *f = callee.u.f;
            Env *local = env_new(f->closure);
            if (have_self) env_declare(local, "self", self_val, 0, 1);
            for (int i = 0; i < f->nparams; i++) {
                const char *pname = f->params[i]->u.ident.name;
                Value v = i < nargs ? args[i] : v_undef();
                env_declare(local, pname, v, 1, 1);
            }
            eval_node(I, local, f->body);
            if (I->ret_set) { result = I->ret_val; I->ret_set = 0; I->ret_val = v_undef(); }
        } else {
            db_error("cannot call %s", v_typename(callee));
        }
        free(args);
        return result;
    }

    case N_LAMBDA: {
        Fn *f = xcalloc(1, sizeof *f);
        f->params  = n->u.fn.params;
        f->nparams = n->u.fn.nparams;
        f->body    = n->u.fn.body;
        f->closure = env;
        f->name    = n->u.fn.name ? xstrdup(n->u.fn.name) : NULL;
        return v_fn(f);
    }

    case N_ASSIGN: {
        Value v = eval_node(I, env, n->u.assign.val);
        env_assign(env, n->u.assign.name, v);
        run_watchers(I);
        return v;
    }

    case N_INDEX_SET: {
        /* If the target is a direct identifier, check value_mutable. */
        if (n->u.idxset.target->kind == N_IDENT) {
            Slot *s = env_find(env, n->u.idxset.target->u.ident.name);
            if (s && !s->value_mutable)
                db_error("cannot mutate contents of '%s' (declared const-const/var-const)",
                         n->u.idxset.target->u.ident.name);
        }
        Value target = eval_node(I, env, n->u.idxset.target);
        Value idx    = eval_node(I, env, n->u.idxset.index);
        Value v      = eval_node(I, env, n->u.idxset.val);
        if (target.t == V_ARR) {
            if (idx.t != V_NUM) db_error("array index must be a number");
            long i = (long)idx.u.num + 1;
            if (i < 0) db_error("array index out of range");
            /* grow if needed */
            while ((size_t)i >= target.u.a->len) arr_push(target.u.a, v_undef());
            target.u.a->items[i] = v;
        } else if (target.t == V_OBJ) {
            if (idx.t != V_STR) db_error("object key must be a string");
            obj_set(target.u.o, idx.u.s->data, v);
        } else if (target.t == V_INST) {
            if (idx.t != V_STR) db_error("instance field name must be a string");
            Slot *s = env_find_local(target.u.i->fields, idx.u.s->data);
            if (!s) env_declare(target.u.i->fields, idx.u.s->data, v, 1, 1);
            else s->v = v;
        } else {
            db_error("cannot set index on %s", v_typename(target));
        }
        run_watchers(I);
        return v;
    }

    case N_MEMBER_SET: {
        if (n->u.memset_.target->kind == N_IDENT) {
            Slot *s = env_find(env, n->u.memset_.target->u.ident.name);
            if (s && !s->value_mutable)
                db_error("cannot mutate contents of '%s' (declared const-const/var-const)",
                         n->u.memset_.target->u.ident.name);
        }
        Value target = eval_node(I, env, n->u.memset_.target);
        Value v      = eval_node(I, env, n->u.memset_.val);
        if (target.t == V_OBJ) obj_set(target.u.o, n->u.memset_.member, v);
        else if (target.t == V_INST) {
            Slot *s = env_find_local(target.u.i->fields, n->u.memset_.member);
            if (!s) env_declare(target.u.i->fields, n->u.memset_.member, v, 1, 1);
            else s->v = v;
        } else db_error("cannot set member on %s", v_typename(target));
        run_watchers(I);
        return v;
    }

    case N_DECL: {
        Value v = n->u.decl.init ? eval_node(I, env, n->u.decl.init) : v_undef();
        if (v.t != V_UNDEF && is_type_deleted(I, v_typename(v)))
            db_error("type '%s' has been deleted", v_typename(v));
        int reassignable  = (n->u.decl.dk == DK_VC || n->u.decl.dk == DK_VV);
        int value_mutable = (n->u.decl.dk == DK_CV || n->u.decl.dk == DK_VV);
        Slot *s = env_declare(env, n->u.decl.name, v, reassignable, value_mutable);
        Lifetime lt = n->u.decl.lt;
        if (lt.kind == LT_DEAD) {
            s->deleted = 1;
        } else if (lt.kind == LT_LINES) {
            s->lt_kind     = LT_LINES;
            /* "lives for N more statements" includes the N reads after
             * this declaration; we add 1 to account for the bump that
             * happens at the end of the declaration's own statement. */
            s->expire_line = I->line_counter + (long)lt.n + 1;
            interp_register_lifetime(I, s);
        } else if (lt.kind == LT_SECONDS) {
            s->lt_kind     = LT_SECONDS;
            s->expire_time = interp_now() + lt.n;
            interp_register_lifetime(I, s);
        }
        run_watchers(I);
        return v;
    }

    case N_FN_DECL: {
        Fn *f = xcalloc(1, sizeof *f);
        f->params  = n->u.fndecl.params;
        f->nparams = n->u.fndecl.nparams;
        f->body    = n->u.fndecl.body;
        f->closure = env;
        f->name    = xstrdup(n->u.fndecl.name);
        env_declare(env, n->u.fndecl.name, v_fn(f), 0, 0);
        return v_undef();
    }

    case N_CLASS_DECL: {
        Class *c = xcalloc(1, sizeof *c);
        c->name         = xstrdup(n->u.cls.name);
        c->body         = n->u.cls.body;
        c->closure      = env;
        c->instance_cap = n->u.cls.instance_cap;
        env_declare(env, n->u.cls.name, v_class(c), 0, 0);
        return v_undef();
    }

    case N_NEW: {
        Slot *s = env_find(env, n->u.newc.name);
        if (!s || s->v.t != V_CLASS) db_error("unknown class '%s'", n->u.newc.name);
        Class *c = s->v.u.c;
        if (c->instance_count >= c->instance_cap)
            db_error("class '%s' already has the maximum %d instances", c->name, c->instance_cap);
        c->instance_count++;
        Inst *inst = xcalloc(1, sizeof *inst);
        inst->cls = c;
        inst->fields = env_new(c->closure);
        /* Evaluate the class body statements directly in inst->fields so
         * declarations populate the instance rather than a throwaway scope. */
        if (c->body && c->body->kind == N_BLOCK) {
            for (int i = 0; i < c->body->u.block.n; i++) {
                eval_node(I, inst->fields, c->body->u.block.stmts[i]);
                if (I->ret_set) { I->ret_set = 0; I->ret_val = v_undef(); break; }
            }
        } else {
            eval_node(I, inst->fields, c->body);
        }
        /* If there's a 'constructor' method, call it with the args. */
        Slot *ctor = env_find_local(inst->fields, "constructor");
        Value iv = v_inst(inst);
        if (ctor && ctor->v.t == V_FN) {
            Fn *f = ctor->v.u.f;
            Env *local = env_new(f->closure);
            env_declare(local, "self", iv, 0, 1);
            for (int i = 0; i < f->nparams; i++) {
                const char *pname = f->params[i]->u.ident.name;
                Value arg = i < n->u.newc.nargs ? eval_node(I, env, n->u.newc.args[i]) : v_undef();
                env_declare(local, pname, arg, 1, 1);
            }
            eval_node(I, local, f->body);
            if (I->ret_set) { I->ret_set = 0; I->ret_val = v_undef(); }
        }
        return iv;
    }

    case N_IF: {
        Value c = eval_node(I, env, n->u.ifs.cond);
        if (v_truthy_det(c)) return eval_node(I, env, n->u.ifs.then);
        else if (n->u.ifs.els) return eval_node(I, env, n->u.ifs.els);
        return v_undef();
    }

    case N_WHILE: {
        while (1) {
            Value c = eval_node(I, env, n->u.whl.cond);
            if (!v_truthy_det(c)) break;
            eval_node(I, env, n->u.whl.body);
            if (I->ret_set) break;
        }
        return v_undef();
    }

    case N_RETURN: {
        I->ret_val = n->u.ret.val ? eval_node(I, env, n->u.ret.val) : v_undef();
        I->ret_set = 1;
        return I->ret_val;
    }

    case N_BLOCK: {
        Env *local = env_new(env);
        Value last = v_undef();
        for (int i = 0; i < n->u.block.n; i++) {
            last = eval_node(I, local, n->u.block.stmts[i]);
            if (I->ret_set) return last;
        }
        return last;
    }

    case N_PROGRAM: {
        Value last = v_undef();
        for (int i = 0; i < n->u.block.n; i++) {
            last = eval_node(I, env, n->u.block.stmts[i]);
            if (I->ret_set) break;
        }
        return last;
    }

    case N_STMT: {
        Value v = eval_node(I, env, n->u.stmt.inner);
        if (n->u.stmt.debug && !I->ret_set) {
            /* '?' terminator: log the expression and its value */
            fputs("[debug] ", stderr);
            v_print(stderr, v);
            fputc('\n', stderr);
        }
        if (n->u.stmt.bangs >= 3 && !I->ret_set) {
            fputs("[!!!] ", stderr);
            v_print(stderr, v);
            fputc('\n', stderr);
        }
        I->line_counter++;
        interp_sweep_lifetimes(I);
        return v;
    }

    case N_PREVIOUS: {
        Slot *s = env_find(env, n->u.prev.name);
        if (!s) db_error("undefined variable '%s'", n->u.prev.name);
        return s->has_prev ? s->prev : v_undef();
    }

    case N_NEXT: {
        /* Best-effort: returns the current value; will update after the next write. */
        Slot *s = env_find(env, n->u.nxt.name);
        if (!s) db_error("undefined variable '%s'", n->u.nxt.name);
        return s->v;
    }

    case N_WHEN: {
        register_watcher(I, n->u.when.cond, n->u.when.body, env);
        /* Evaluate immediately so if it's already true, it fires at registration. */
        Value c = eval_node(I, env, n->u.when.cond);
        Bool3 now = v_truthy(c);
        Watcher *w = I->watchers[I->nwatchers - 1];
        w->last = now;
        if (now == B_TRUE) eval_node(I, env, n->u.when.body);
        return v_undef();
    }

    case N_DELETE: {
        Node *t = n->u.del.target;
        if (t->kind == N_IDENT) {
            /* Could be a type name or a variable. */
            const char *nm = t->u.ident.name;
            if (strcmp(nm, "number") == 0 || strcmp(nm, "string") == 0 ||
                strcmp(nm, "boolean") == 0 || strcmp(nm, "array") == 0 ||
                strcmp(nm, "object") == 0 || strcmp(nm, "function") == 0) {
                del_type(I, nm);
                return v_undef();
            }
            Slot *s = env_find(env, nm);
            if (!s) db_error("cannot delete unknown '%s'", nm);
            free_value_payload(s->v);
            s->deleted = 1;
            return v_undef();
        }
        if (t->kind == N_LIT_NUM) {
            del_num(I, t->u.num);
            return v_undef();
        }
        if (t->kind == N_LIT_STR) {
            del_str(I, t->u.str.data, t->u.str.len);
            return v_undef();
        }
        if (t->kind == N_MEMBER) {
            Value tv = eval_node(I, env, t->u.member.target);
            if (tv.t == V_OBJ) {
                /* remove key */
                ObjEntry **pp = &tv.u.o->head;
                while (*pp) {
                    if (strcmp((*pp)->key, t->u.member.name) == 0) {
                        ObjEntry *dead = *pp;
                        *pp = dead->next;
                        free(dead->key);
                        free(dead->val);
                        free(dead);
                        break;
                    }
                    pp = &(*pp)->next;
                }
                return v_undef();
            }
        }
        db_error("cannot delete this kind of expression");
    }
    }
    return v_undef();
}

void interp_run(Interp *I, Node *program) {
    eval_node(I, I->globals, program);
}
