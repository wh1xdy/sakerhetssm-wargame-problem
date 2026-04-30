#ifndef DB_COMMON_H
#define DB_COMMON_H

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Forward decls shared across modules. */
typedef struct Str     Str;
typedef struct Arr     Arr;
typedef struct Obj     Obj;
typedef struct Fn      Fn;
typedef struct Class   Class;
typedef struct Inst    Inst;
typedef struct Builtin Builtin;
typedef struct Value   Value;
typedef struct Node    Node;
typedef struct Env     Env;
typedef struct Slot    Slot;
typedef struct Watcher Watcher;
typedef struct Interp  Interp;

/* Dynamic byte buffer. */
typedef struct {
    char  *data;
    size_t len;
    size_t cap;
} Buf;

void buf_init(Buf *b);
void buf_push(Buf *b, char c);
void buf_append(Buf *b, const char *s, size_t n);
void buf_free(Buf *b);

/* Allocation helpers that abort on OOM. */
void *xmalloc(size_t n);
void *xcalloc(size_t nmemb, size_t size);
void *xrealloc(void *p, size_t n);
char *xstrndup(const char *s, size_t n);
char *xstrdup(const char *s);

/* Slop heap: next allocation of exactly `n` bytes reuses `p` (see docs/DreamSlop.md). */
void slop_recycle_next_alloc(void *p, size_t n);

/* Fatal error helper (used for parse/eval errors). Longjmps back to the
 * top-level in the interpreter when one is installed; otherwise exits. */
void db_error(const char *fmt, ...) __attribute__((noreturn, format(printf, 1, 2)));

/* Set/clear the error landing pad. */
#include <setjmp.h>
extern jmp_buf *db_errjmp;
extern char     db_errmsg[512];

#endif
