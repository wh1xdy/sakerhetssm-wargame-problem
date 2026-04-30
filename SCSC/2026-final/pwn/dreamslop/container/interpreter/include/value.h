#ifndef DB_VALUE_H
#define DB_VALUE_H

#include "common.h"

typedef enum {
    V_UNDEF,
    V_NUM,
    V_STR,
    V_BOOL,
    V_ARR,
    V_OBJ,
    V_FN,
    V_CLASS,
    V_INST,
    V_BUILTIN,
} VType;

typedef enum { B_FALSE = 0, B_TRUE = 1, B_MAYBE = 2 } Bool3;

struct Str {
    size_t len;
    char  *data;
};

struct Arr {
    size_t  len, cap;
    Value  *items;
};

typedef struct ObjEntry {
    char            *key;
    Value           *val;
    struct ObjEntry *next;
} ObjEntry;

struct Obj {
    ObjEntry *head;
};

struct Fn {
    Node **params;      /* NIdent nodes */
    int    nparams;
    Node  *body;        /* may be NULL for arrow => expr (expr stored in body as NBlock/NExpr) */
    Env   *closure;
    char  *name;        /* optional */
};

struct Class {
    char *name;
    Node *body;         /* NBlock containing declarations */
    Env  *closure;
    int   instance_count;
    int   instance_cap; /* 2 by default */
};

struct Inst {
    Class *cls;
    Env   *fields;      /* an env with the instance's own slots */
};

typedef Value (*BuiltinFn)(Interp *I, Value *args, int nargs);

struct Builtin {
    const char *name;
    BuiltinFn   fn;
};

struct Value {
    VType t;
    union {
        double   num;
        Str     *s;
        Bool3    b;
        Arr     *a;
        Obj     *o;
        Fn      *f;
        Class   *c;
        Inst    *i;
        Builtin *bi;
    } u;
};

/* Constructors. All heap data is leaked (tree-walker, small programs). */
Value v_undef(void);
Value v_num(double x);
Value v_bool(Bool3 b);
Value v_str(const char *s);
Value v_strn(const char *s, size_t n);
Value v_str_take(char *s, size_t n); /* takes ownership */
Value v_arr(void);
Value v_obj(void);
Value v_fn(Fn *f);
Value v_class(Class *c);
Value v_inst(Inst *i);
Value v_builtin(Builtin *b);

/* Array/object helpers. */
void    arr_push(Arr *a, Value v);
Value  *obj_get(Obj *o, const char *key);   /* NULL if missing */
void    obj_set(Obj *o, const char *key, Value v);

/* Truthiness and comparison. */
Bool3 v_truthy(Value v);            /* Kleene: maybe stays maybe */
int   v_truthy_det(Value v);        /* forces maybe by coin flip */
int   v_eq_loose(Value a, Value b, Bool3 *out_maybe);
int   v_eq_value(Value a, Value b); /* ==== */
int   v_eq_ref(Value a, Value b);   /* ===== */

/* Printing. */
void  v_print(FILE *f, Value v);
void  v_print_raw(FILE *f, Value v); /* strings unquoted */
const char *v_typename(Value v);

/* String concat helper. */
Value v_str_concat(Value a, Value b);

#endif
