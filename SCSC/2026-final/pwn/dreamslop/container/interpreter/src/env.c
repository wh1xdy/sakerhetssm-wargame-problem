#include "env.h"

Env *env_new(Env *parent) {
    Env *e = xcalloc(1, sizeof *e);
    e->parent = parent;
    return e;
}

Slot *env_find_local(Env *e, const char *name) {
    for (Slot *s = e->slots; s; s = s->next)
        if (strcmp(s->name, name) == 0) return s;
    return NULL;
}

Slot *env_find(Env *e, const char *name) {
    for (; e; e = e->parent) {
        Slot *s = env_find_local(e, name);
        if (s) return s;
    }
    return NULL;
}

Slot *env_declare(Env *e, const char *name, Value v, int reassignable, int value_mutable) {
    Slot *s = env_find_local(e, name);
    if (s) {
        if (s->deleted) {
            /* re-declaration after delete resurrects */
            s->deleted = 0;
            s->v = v;
            s->reassignable  = reassignable;
            s->value_mutable = value_mutable;
            s->has_prev = 0;
            return s;
        }
        db_error("variable '%s' already declared", name);
    }
    s = xcalloc(1, sizeof *s);
    s->name          = xstrdup(name);
    s->v             = v;
    s->reassignable  = reassignable;
    s->value_mutable = value_mutable;
    s->next          = e->slots;
    e->slots         = s;
    return s;
}

void env_assign(Env *e, const char *name, Value v) {
    Slot *s = env_find(e, name);
    if (!s) db_error("undefined variable '%s'", name);
    if (s->deleted) db_error("variable '%s' has been deleted", name);
    if (!s->reassignable) db_error("cannot reassign const variable '%s'", name);
    s->prev     = s->v;
    s->has_prev = 1;
    s->v        = v;
}
