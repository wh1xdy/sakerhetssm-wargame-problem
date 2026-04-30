#ifndef DB_PARSER_H
#define DB_PARSER_H

#include "common.h"
#include "lexer.h"
#include "value.h"

typedef enum {
    N_LIT_NUM, N_LIT_STR, N_LIT_BOOL, N_LIT_UNDEF,
    N_IDENT,
    N_TEMPLATE,
    N_ARRAY,
    N_OBJECT,
    N_UNARY,
    N_BINOP,
    N_INDEX,
    N_MEMBER,
    N_CALL,
    N_LAMBDA,
    N_ASSIGN,
    N_INDEX_SET,
    N_MEMBER_SET,
    N_DECL,
    N_FN_DECL,
    N_CLASS_DECL,
    N_NEW,
    N_IF, N_WHILE, N_RETURN,
    N_BLOCK,
    N_STMT,
    N_PREVIOUS, N_NEXT, N_WHEN, N_DELETE,
    N_PROGRAM,
} NKind;

typedef enum { DK_CC, DK_CV, DK_VC, DK_VV } DeclKind;

/* Lifetime spec attached to a declaration. */
typedef enum {
    LT_INF,         /* infinite (default) */
    LT_DEAD,        /* never (e.g. <-Infinity>) */
    LT_LINES,       /* expires after N more lines/statements */
    LT_SECONDS,     /* expires after N seconds wall-clock */
} LifetimeKind;

typedef struct {
    LifetimeKind kind;
    double       n;
} Lifetime;

/* Binary operator codes. */
typedef enum {
    OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_MOD,
    OP_LT, OP_GT, OP_LE, OP_GE,
    OP_AND, OP_OR,
    OP_EQ2, OP_EQ3, OP_EQ4, OP_EQ5,
} BinOp;

typedef enum { UN_NEG, UN_NOT } UnOp;

struct Node {
    NKind kind;
    int   line;
    union {
        double num;
        struct { char *data; size_t len; } str;
        Bool3  boolv;
        struct { char *name; } ident;
        struct { Node **items; int n; } arr;
        struct { char **keys; Node **vals; int n; } obj;
        struct { UnOp op; Node *a; } un;
        struct { BinOp op; Node *a, *b; } bin;
        struct { Node *a, *b; } pair;
        struct { Node *callee; Node **args; int nargs; } call;
        struct { Node *target; char *name; } member;
        struct { Node **params; int nparams; Node *body; char *name; } fn;
        struct { char *name; Node **params; int nparams; Node *body; } fndecl;
        struct { char *name; Node *body; int instance_cap; } cls;
        struct { char *name; Node **args; int nargs; } newc;
        struct { Node *cond, *then, *els; } ifs;
        struct { Node *cond, *body; } whl;
        struct { Node *val; } ret;
        struct { Node **stmts; int n; } block;
        struct { Node *inner; int bangs; int debug; } stmt;
        struct { DeclKind dk; char *name; Node *init; Lifetime lt; } decl;
        struct { char *name; Node *val; } assign;
        struct { Node *target; Node *index; Node *val; } idxset;
        struct { Node *target; char *member; Node *val; } memset_;
        struct { Node *cond; Node *body; } when;
        struct { Node *target; } del;
        struct { char *name; } prev;
        struct { char *name; } nxt;
    } u;
};

Node *parse_program(const char *src, size_t len);

/* Helpers used by the evaluator. */
const char *binop_name(BinOp op);

#endif
