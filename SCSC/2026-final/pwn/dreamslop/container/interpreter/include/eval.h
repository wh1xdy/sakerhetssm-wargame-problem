#ifndef DB_EVAL_H
#define DB_EVAL_H

#include "common.h"
#include "parser.h"
#include "env.h"
#include "value.h"

struct Watcher {
    Node    *cond;
    Node    *body;
    Env     *env;
    Bool3    last;     /* last observed truthiness */
    int      fired;    /* has it fired at least once? */
};

struct Interp {
    Env    *globals;
    /* reactive "when" watchers, in declaration order */
    Watcher **watchers;
    int       nwatchers;
    int       cap_watchers;

    /* delete machinery */
    /* deleted literal numbers */
    double *del_nums; int n_del_nums, cap_del_nums;
    /* deleted literal strings */
    char  **del_strs; int n_del_strs, cap_del_strs;
    /* deleted type names ("number","string",...) */
    char  **del_types; int n_del_types, cap_del_types;

    /* return signalling */
    int    ret_set;
    Value  ret_val;

    /* Lifetime tracking: every executed statement bumps line_counter.
     * After each statement we sweep `lt_slots` for expirations. */
    long     line_counter;
    Slot   **lt_slots;
    int      n_lt_slots, cap_lt_slots;
};

/* Register a slot for lifetime-based expiration. */
void interp_register_lifetime(Interp *I, Slot *s);
/* Sweep lifetime slots and mark expired ones as deleted. */
void interp_sweep_lifetimes(Interp *I);
/* Current monotonic-ish time in seconds. */
double interp_now(void);

Interp *interp_new(void);
void    interp_run(Interp *I, Node *program);

/* Used by eval + builtins */
Value   eval_node(Interp *I, Env *env, Node *n);
void    run_watchers(Interp *I);

/* Delete helpers */
int is_num_deleted(Interp *I, double x);
int is_str_deleted(Interp *I, const char *s, size_t n);
int is_type_deleted(Interp *I, const char *name);

#endif
