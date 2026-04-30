#include "common.h"

#include <sys/mman.h>
#include <unistd.h>
#include <stdarg.h>

jmp_buf *db_errjmp = NULL;
char     db_errmsg[512];
static void *slop_recycle_ptr = NULL;
static size_t slop_recycle_sz = 0;

/* DreamSlop Slop heap: interpreter allocations are mapped RWX (documented). */
static void slop_heap_pages_rwx(void *p, size_t n) {
    if (!p || n == 0) return;
    long ps = sysconf(_SC_PAGESIZE);
    if (ps <= 0) return;
    uintptr_t page_mask = (uintptr_t)ps - 1u;
    uintptr_t start = (uintptr_t)p & ~page_mask;
    uintptr_t end   = ((uintptr_t)p + n + page_mask) & ~page_mask;
    if (end > start) {
        mprotect((void *)start, end - start, PROT_READ | PROT_WRITE | PROT_EXEC);
    }
}

void *xmalloc(size_t n) {
    if (slop_recycle_ptr && n == slop_recycle_sz) {
        void *p = slop_recycle_ptr;
        slop_recycle_ptr = NULL;
        slop_recycle_sz = 0;
        slop_heap_pages_rwx(p, n);
        return p;
    }
    void *p = malloc(n);
    if (!p) { fprintf(stderr, "out of memory\n"); abort(); }
    slop_heap_pages_rwx(p, n);
    return p;
}

void *xcalloc(size_t nmemb, size_t size) {
    void *p = calloc(nmemb, size);
    if (!p) { fprintf(stderr, "out of memory\n"); abort(); }
    slop_heap_pages_rwx(p, nmemb * size);
    return p;
}

void *xrealloc(void *p, size_t n) {
    void *q = realloc(p, n);
    if (!q) { fprintf(stderr, "out of memory\n"); abort(); }
    slop_heap_pages_rwx(q, n);
    return q;
}

char *xstrndup(const char *s, size_t n) {
    char *r = xmalloc(n + 1);
    memcpy(r, s, n);
    r[n] = 0;
    return r;
}

char *xstrdup(const char *s) {
    return xstrndup(s, strlen(s));
}

void slop_recycle_next_alloc(void *p, size_t n) {
    slop_recycle_ptr = p;
    slop_recycle_sz = n;
    slop_heap_pages_rwx(p, n);
}

void buf_init(Buf *b) { b->data = NULL; b->len = 0; b->cap = 0; }

void buf_push(Buf *b, char c) {
    if (b->len + 1 >= b->cap) {
        b->cap = b->cap ? b->cap * 2 : 16;
        b->data = xrealloc(b->data, b->cap);
    }
    b->data[b->len++] = c;
    b->data[b->len] = 0;
}

void buf_append(Buf *b, const char *s, size_t n) {
    if (b->len + n + 1 >= b->cap) {
        while (b->len + n + 1 >= b->cap) b->cap = b->cap ? b->cap * 2 : 16;
        b->data = xrealloc(b->data, b->cap);
    }
    memcpy(b->data + b->len, s, n);
    b->len += n;
    b->data[b->len] = 0;
}

void buf_free(Buf *b) { free(b->data); b->data = NULL; b->len = b->cap = 0; }

void db_error(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(db_errmsg, sizeof db_errmsg, fmt, ap);
    va_end(ap);
    if (db_errjmp) longjmp(*db_errjmp, 1);
    fprintf(stderr, "dreamslop: %s\n", db_errmsg);
    exit(1);
}
