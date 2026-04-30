#include "value.h"

#include <math.h>
#include <stdio.h>
#include <time.h>

static int rng_seeded = 0;

static int coin(void) {
    if (!rng_seeded) { srand((unsigned)time(NULL)); rng_seeded = 1; }
    return rand() & 1;
}

Value v_undef(void)         { Value v = { .t = V_UNDEF }; return v; }
Value v_num(double x)       { Value v = { .t = V_NUM };  v.u.num = x; return v; }
Value v_bool(Bool3 b)       { Value v = { .t = V_BOOL }; v.u.b = b; return v; }

Value v_strn(const char *s, size_t n) {
    Str *str = xmalloc(sizeof *str);
    str->len  = n;
    str->data = xmalloc(n + 1);
    memcpy(str->data, s, n);
    str->data[n] = 0;
    Value v = { .t = V_STR };
    v.u.s = str;
    return v;
}

Value v_str(const char *s) { return v_strn(s, strlen(s)); }

Value v_str_take(char *s, size_t n) {
    Str *str = xmalloc(sizeof *str);
    str->len  = n;
    str->data = s;
    Value v = { .t = V_STR };
    v.u.s = str;
    return v;
}

Value v_arr(void) {
    Arr *a = xcalloc(1, sizeof *a);
    Value v = { .t = V_ARR };
    v.u.a = a;
    return v;
}

Value v_obj(void) {
    Obj *o = xcalloc(1, sizeof *o);
    Value v = { .t = V_OBJ };
    v.u.o = o;
    return v;
}

Value v_fn(Fn *f)        { Value v = { .t = V_FN };    v.u.f = f; return v; }
Value v_class(Class *c)  { Value v = { .t = V_CLASS }; v.u.c = c; return v; }
Value v_inst(Inst *i)    { Value v = { .t = V_INST };  v.u.i = i; return v; }
Value v_builtin(Builtin *b) { Value v = { .t = V_BUILTIN }; v.u.bi = b; return v; }

void arr_push(Arr *a, Value v) {
    if (a->len + 1 > a->cap) {
        a->cap = a->cap ? a->cap * 2 : 4;
        a->items = xrealloc(a->items, a->cap * sizeof *a->items);
    }
    a->items[a->len++] = v;
}

Value *obj_get(Obj *o, const char *key) {
    for (ObjEntry *e = o->head; e; e = e->next)
        if (strcmp(e->key, key) == 0) return e->val;
    return NULL;
}

void obj_set(Obj *o, const char *key, Value v) {
    for (ObjEntry *e = o->head; e; e = e->next) {
        if (strcmp(e->key, key) == 0) { *e->val = v; return; }
    }
    ObjEntry *e = xmalloc(sizeof *e);
    e->key  = xstrdup(key);
    e->val  = xmalloc(sizeof *e->val);
    *e->val = v;
    e->next = o->head;
    o->head = e;
}

Bool3 v_truthy(Value v) {
    switch (v.t) {
    case V_UNDEF:   return B_FALSE;
    case V_NUM:     return v.u.num != 0.0 ? B_TRUE : B_FALSE;
    case V_BOOL:    return v.u.b;
    case V_STR:     return v.u.s->len ? B_TRUE : B_FALSE;
    case V_ARR:     return v.u.a->len ? B_TRUE : B_FALSE;
    case V_OBJ:
    case V_FN:
    case V_CLASS:
    case V_INST:
    case V_BUILTIN: return B_TRUE;
    }
    return B_FALSE;
}

int v_truthy_det(Value v) {
    Bool3 b = v_truthy(v);
    if (b == B_MAYBE) return coin();
    return b == B_TRUE;
}

static int nums_equal(double x, double y) {
    if (isnan(x) || isnan(y)) return 0;
    return x == y;
}

int v_eq_value(Value a, Value b) {
    if (a.t != b.t) return 0;
    switch (a.t) {
    case V_UNDEF: return 1;
    case V_NUM:   return nums_equal(a.u.num, b.u.num);
    case V_BOOL:  return a.u.b == b.u.b;
    case V_STR:
        return a.u.s->len == b.u.s->len &&
               memcmp(a.u.s->data, b.u.s->data, a.u.s->len) == 0;
    case V_ARR:   return a.u.a == b.u.a;
    case V_OBJ:   return a.u.o == b.u.o;
    case V_FN:    return a.u.f == b.u.f;
    case V_CLASS: return a.u.c == b.u.c;
    case V_INST:  return a.u.i == b.u.i;
    case V_BUILTIN: return a.u.bi == b.u.bi;
    }
    return 0;
}

int v_eq_ref(Value a, Value b) {
    if (a.t != b.t) return 0;
    switch (a.t) {
    case V_STR:   return a.u.s == b.u.s;
    case V_ARR:   return a.u.a == b.u.a;
    case V_OBJ:   return a.u.o == b.u.o;
    case V_FN:    return a.u.f == b.u.f;
    case V_CLASS: return a.u.c == b.u.c;
    case V_INST:  return a.u.i == b.u.i;
    case V_BUILTIN: return a.u.bi == b.u.bi;
    default:      return v_eq_value(a, b);
    }
}

/* Loose == : numeric coerce strings, maybe propagates. */
int v_eq_loose(Value a, Value b, Bool3 *out_maybe) {
    *out_maybe = B_FALSE;
    if (a.t == V_BOOL && a.u.b == B_MAYBE) { *out_maybe = B_MAYBE; return 0; }
    if (b.t == V_BOOL && b.u.b == B_MAYBE) { *out_maybe = B_MAYBE; return 0; }
    if (a.t == b.t) return v_eq_value(a, b);
    /* num <-> string */
    if ((a.t == V_NUM && b.t == V_STR) || (a.t == V_STR && b.t == V_NUM)) {
        const char *s = a.t == V_STR ? a.u.s->data : b.u.s->data;
        double      n = a.t == V_NUM ? a.u.num : b.u.num;
        char *end = NULL;
        double d = strtod(s, &end);
        if (end && *end == 0) return nums_equal(d, n);
        return 0;
    }
    /* bool <-> num */
    if ((a.t == V_BOOL && b.t == V_NUM) || (a.t == V_NUM && b.t == V_BOOL)) {
        double bn = a.t == V_BOOL ? (a.u.b == B_TRUE ? 1.0 : 0.0) : (b.u.b == B_TRUE ? 1.0 : 0.0);
        double nm = a.t == V_NUM  ? a.u.num : b.u.num;
        return nums_equal(bn, nm);
    }
    /* undef <-> undef only */
    return 0;
}

const char *v_typename(Value v) {
    switch (v.t) {
    case V_UNDEF:   return "undefined";
    case V_NUM:     return "number";
    case V_STR:     return "string";
    case V_BOOL:    return "boolean";
    case V_ARR:     return "array";
    case V_OBJ:     return "object";
    case V_FN:      return "function";
    case V_CLASS:   return "class";
    case V_INST:    return "instance";
    case V_BUILTIN: return "builtin";
    }
    return "?";
}

static void print_num(FILE *f, double x) {
    if (x == 0.0 && signbit(x)) { fputs("-0", f); return; }
    if (isnan(x)) { fputs("NaN", f); return; }
    if (isinf(x)) { fputs(x < 0 ? "-Infinity" : "Infinity", f); return; }
    if (x == (double)(long long)x && fabs(x) < 1e16)
        fprintf(f, "%lld", (long long)x);
    else
        fprintf(f, "%g", x);
}

static void print_str_quoted(FILE *f, Str *s) {
    fputc('"', f);
    for (size_t i = 0; i < s->len; i++) {
        char c = s->data[i];
        switch (c) {
        case '\n': fputs("\\n", f); break;
        case '\t': fputs("\\t", f); break;
        case '\\': fputs("\\\\", f); break;
        case '"':  fputs("\\\"", f); break;
        default:   fputc(c, f);
        }
    }
    fputc('"', f);
}

void v_print(FILE *f, Value v) {
    switch (v.t) {
    case V_UNDEF: fputs("undefined", f); break;
    case V_NUM:   print_num(f, v.u.num); break;
    case V_STR:   print_str_quoted(f, v.u.s); break;
    case V_BOOL:
        fputs(v.u.b == B_TRUE ? "true" : v.u.b == B_FALSE ? "false" : "maybe", f);
        break;
    case V_ARR: {
        fputc('[', f);
        for (size_t i = 0; i < v.u.a->len; i++) {
            if (i) fputs(", ", f);
            v_print(f, v.u.a->items[i]);
        }
        fputc(']', f);
        break;
    }
    case V_OBJ: {
        fputc('{', f);
        int first = 1;
        for (ObjEntry *e = v.u.o->head; e; e = e->next) {
            if (!first) fputs(", ", f);
            first = 0;
            fprintf(f, "%s: ", e->key);
            v_print(f, *e->val);
        }
        fputc('}', f);
        break;
    }
    case V_FN:      fprintf(f, "<function %s>", v.u.f->name ? v.u.f->name : "anon"); break;
    case V_CLASS:   fprintf(f, "<class %s>", v.u.c->name); break;
    case V_INST:    fprintf(f, "<%s instance>", v.u.i->cls->name ? v.u.i->cls->name : "anon"); break;
    case V_BUILTIN: fprintf(f, "<builtin %s>", v.u.bi->name); break;
    }
}

void v_print_raw(FILE *f, Value v) {
    if (v.t == V_STR) fwrite(v.u.s->data, 1, v.u.s->len, f);
    else v_print(f, v);
}

static void append_value_raw(Buf *buf, Value v) {
    if (v.t == V_STR) { buf_append(buf, v.u.s->data, v.u.s->len); return; }
    char *mem = NULL;
    size_t n = 0;
    FILE *f = open_memstream(&mem, &n);
    if (!f) return;
    v_print(f, v);
    fclose(f);
    buf_append(buf, mem, n);
    free(mem);
}

Value v_str_concat(Value a, Value b) {
    Buf buf; buf_init(&buf);
    append_value_raw(&buf, a);
    append_value_raw(&buf, b);
    if (!buf.data) { buf.data = xmalloc(1); buf.data[0] = 0; }
    return v_str_take(buf.data, buf.len);
}
