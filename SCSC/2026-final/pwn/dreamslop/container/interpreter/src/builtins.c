#include "builtins.h"

#include <math.h>

static Value b_print(Interp *I, Value *args, int nargs) {
    (void)I;
    for (int i = 0; i < nargs; i++) {
        if (i) fputc(' ', stdout);
        v_print_raw(stdout, args[i]);
    }
    fputc('\n', stdout);
    return v_undef();
}

static Value b_input(Interp *I, Value *args, int nargs) {
    (void)I;
    if (nargs >= 1) v_print_raw(stdout, args[0]);
    fflush(stdout);
    Buf b; buf_init(&b);
    int c;
    while ((c = fgetc(stdin)) != EOF && c != '\n') buf_push(&b, (char)c);
    if (!b.data) { b.data = xmalloc(1); b.data[0] = 0; }
    return v_str_take(b.data, b.len);
}

static Value b_typeof(Interp *I, Value *args, int nargs) {
    (void)I;
    if (nargs < 1) return v_str("undefined");
    return v_str(v_typename(args[0]));
}

static Value b_len(Interp *I, Value *args, int nargs) {
    (void)I;
    if (nargs < 1) return v_num(0);
    Value v = args[0];
    if (v.t == V_STR) return v_num((double)v.u.s->len);
    if (v.t == V_ARR) return v_num((double)v.u.a->len);
    if (v.t == V_OBJ) {
        int n = 0;
        for (ObjEntry *e = v.u.o->head; e; e = e->next) n++;
        return v_num((double)n);
    }
    return v_num(0);
}

static Value b_str(Interp *I, Value *args, int nargs) {
    (void)I;
    if (nargs < 1) return v_str("");
    Value v = args[0];
    if (v.t == V_STR) return v;
    char *mem = NULL; size_t n = 0;
    FILE *f = open_memstream(&mem, &n);
    if (!f) return v_str("");
    v_print(f, v);
    fclose(f);
    return v_str_take(mem, n);
}

static Value b_num(Interp *I, Value *args, int nargs) {
    (void)I;
    if (nargs < 1) return v_num(0);
    Value v = args[0];
    switch (v.t) {
    case V_NUM: return v;
    case V_BOOL: return v_num(v.u.b == B_TRUE ? 1 : v.u.b == B_MAYBE ? 0.5 : 0);
    case V_STR: { char *e = NULL; double d = strtod(v.u.s->data, &e); return v_num(e == v.u.s->data ? NAN : d); }
    default: return v_num(NAN);
    }
}

static Value b_push(Interp *I, Value *args, int nargs) {
    if (nargs < 2 || args[0].t != V_ARR) db_error("push(array, value)");
    arr_push(args[0].u.a, args[1]);
    run_watchers(I);
    return v_num((double)args[0].u.a->len);
}

static Value b_pop(Interp *I, Value *args, int nargs) {
    if (nargs < 1 || args[0].t != V_ARR) db_error("pop(array)");
    Arr *a = args[0].u.a;
    if (a->len == 0) return v_undef();
    Value v = a->items[a->len - 1];
    a->len--;
    run_watchers(I);
    return v;
}

static Value b_floor(Interp *I, Value *args, int nargs) {
    (void)I;
    if (nargs < 1) return v_num(0);
    return v_num(floor(args[0].t == V_NUM ? args[0].u.num : 0));
}

static void register_builtin(Interp *I, const char *name, BuiltinFn fn) {
    Builtin *b = xcalloc(1, sizeof *b);
    b->name = name;
    b->fn   = fn;
    env_declare(I->globals, name, v_builtin(b), 0, 0);
}

void builtins_install(Interp *I) {
    register_builtin(I, "print",  b_print);
    register_builtin(I, "input",  b_input);
    register_builtin(I, "typeof", b_typeof);
    register_builtin(I, "len",    b_len);
    register_builtin(I, "String", b_str);
    register_builtin(I, "Number", b_num);
    register_builtin(I, "push",   b_push);
    register_builtin(I, "pop",    b_pop);
    register_builtin(I, "floor",  b_floor);
}
