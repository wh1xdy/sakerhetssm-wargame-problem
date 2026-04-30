#include "common.h"
#include "lexer.h"
#include "parser.h"
#include "eval.h"
#include "builtins.h"

#include <setjmp.h>

static char *read_file(const char *path, size_t *out_len) {
    FILE *f = fopen(path, "rb");
    if (!f) { fprintf(stderr, "dreamslop: cannot open '%s'\n", path); exit(1); }
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buf = xmalloc((size_t)sz + 1);
    size_t n = fread(buf, 1, (size_t)sz, f);
    buf[n] = 0;
    fclose(f);
    *out_len = n;
    return buf;
}

static int has_suffix(const char *s, const char *suf) {
    size_t ls = strlen(s), lf = strlen(suf);
    return ls >= lf && strcmp(s + ls - lf, suf) == 0;
}

static int run_file(const char *path) {
    if (!has_suffix(path, ".db") && !has_suffix(path, ".dreamberd") &&
        !has_suffix(path, ".\xf0\x9f\x8d\x93")) {
        fprintf(stderr, "dreamslop: warning: '%s' has no DreamSlop extension (.db, .dreamberd, .🍓) -- running anyway\n", path);
    }
    size_t len = 0;
    char *src = read_file(path, &len);
    jmp_buf jb;
    jmp_buf *prev = db_errjmp;
    db_errjmp = &jb;
    int rc = 0;
    if (setjmp(jb) == 0) {
        Node *prog = parse_program(src, len);
        Interp *I = interp_new();
        interp_run(I, prog);
    } else {
        fprintf(stderr, "dreamslop: %s\n", db_errmsg);
        rc = 1;
    }
    db_errjmp = prev;
    free(src);
    return rc;
}

/* Returns 1 if the buffer ends with a bang/question terminator (possibly
 * followed by whitespace). This is the signal the REPL uses to decide
 * whether to keep reading more lines. */
static int ends_with_terminator(const char *s, size_t n) {
    /* Trim trailing whitespace. */
    while (n > 0 && (s[n-1] == ' ' || s[n-1] == '\t' || s[n-1] == '\n' || s[n-1] == '\r')) n--;
    if (n == 0) return 0;
    /* Walk backwards over a run of !/?. */
    size_t i = n;
    int seen = 0;
    while (i > 0 && (s[i-1] == '!' || s[i-1] == '?')) { i--; seen = 1; }
    return seen;
}

static int run_repl(void) {
    printf("DreamSlop REPL -- end statements with '!' (or '?').  Ctrl-D to exit.\n");
    Interp *I = interp_new();
    Buf pending; buf_init(&pending);
    for (;;) {
        fputs(pending.len ? "...  " : "db>  ", stdout);
        fflush(stdout);
        Buf line; buf_init(&line);
        int c;
        int got_any = 0;
        while ((c = fgetc(stdin)) != EOF && c != '\n') { buf_push(&line, (char)c); got_any = 1; }
        if (c == EOF && !got_any && pending.len == 0) { fputc('\n', stdout); break; }
        if (line.len) buf_append(&pending, line.data, line.len);
        buf_push(&pending, '\n');
        buf_free(&line);
        if (!ends_with_terminator(pending.data, pending.len) && c != EOF) continue;

        jmp_buf jb;
        jmp_buf *prev = db_errjmp;
        db_errjmp = &jb;
        if (setjmp(jb) == 0) {
            Node *prog = parse_program(pending.data, pending.len);
            interp_run(I, prog);
        } else {
            fprintf(stderr, "dreamslop: %s\n", db_errmsg);
        }
        db_errjmp = prev;
        buf_free(&pending);
        buf_init(&pending);
        if (c == EOF) break;
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) return run_repl();
    return run_file(argv[1]);
}
