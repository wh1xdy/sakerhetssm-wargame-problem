#ifndef DB_ENV_H
#define DB_ENV_H

#include "common.h"
#include "value.h"

struct Slot {
    char   *name;
    Value   v;
    uint8_t reassignable;   /* outer 'var' */
    uint8_t value_mutable;  /* inner 'var' */
    uint8_t deleted;
    uint8_t has_prev;
    Value   prev;
    /* Lifetime tracking. lt_kind = 0 means infinite (no expiration). */
    int     lt_kind;        /* LifetimeKind from parser.h, or 0 = infinite */
    long    expire_line;    /* for LT_LINES: line counter at which to expire */
    double  expire_time;    /* for LT_SECONDS: monotonic-ish time to expire */
    struct Slot *next;
};

struct Env {
    Slot      *slots;
    struct Env *parent;
};

Env   *env_new(Env *parent);
Slot  *env_find(Env *e, const char *name);         /* searches up the chain */
Slot  *env_find_local(Env *e, const char *name);
Slot  *env_declare(Env *e, const char *name, Value v, int reassignable, int value_mutable);
void   env_assign(Env *e, const char *name, Value v); /* respects var/const; errors on const */

#endif
