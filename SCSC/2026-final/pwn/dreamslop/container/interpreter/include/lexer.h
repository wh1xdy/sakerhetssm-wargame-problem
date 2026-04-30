#ifndef DB_LEXER_H
#define DB_LEXER_H

#include "common.h"

typedef enum {
    TK_EOF = 0,

    TK_NUM,             /* numeric literal */
    TK_STR,             /* plain string literal (no interpolation) */
    TK_STR_CHUNK,       /* chunk of a template string, followed by INTERP_START/END and more chunks */
    TK_INTERP_START,    /* '${' inside a string */
    TK_INTERP_END,      /* '}' that closes an interpolation */
    TK_IDENT,

    /* Keywords */
    TK_CONST, TK_VAR,
    TK_IF, TK_ELSE, TK_WHILE, TK_RETURN,
    TK_TRUE, TK_FALSE, TK_MAYBE, TK_UNDEFINED,
    TK_PREVIOUS, TK_NEXT, TK_WHEN,
    TK_CLASS, TK_NEW, TK_DELETE,
    TK_FN,              /* any non-empty prefix of "function" */

    /* Punctuation / operators */
    TK_LPAREN, TK_RPAREN,
    TK_LBRACE, TK_RBRACE,
    TK_LBRACKET, TK_RBRACKET,
    TK_COMMA,
    TK_DOT,
    TK_COLON,
    TK_ARROW,           /* => */
    TK_PLUS, TK_MINUS, TK_STAR, TK_SLASH, TK_PERCENT,
    TK_LT, TK_GT, TK_LE, TK_GE,
    TK_AND, TK_OR, TK_NOT,
    TK_ASSIGN,          /* =   (one equals) */
    TK_EQ2, TK_EQ3, TK_EQ4, TK_EQ5,
    TK_BANG,            /* statement terminator; carries .ival = count and .debug = has_question */
} TokKind;

typedef struct {
    TokKind  kind;
    const char *start; /* into source buffer */
    size_t   len;
    double   num;
    /* For strings and identifiers: use a copied C-string. */
    char    *text;
    /* For TK_BANG: .ival = number of !, .debug = number of ? (>0 means debug). */
    int      ival;
    int      debug;
    int      line;
} Tok;

typedef struct {
    const char *src;
    size_t      srclen;
    size_t      pos;
    int         line;
    /* stack state for template string interpolation:
     *   depth: number of nested `${` that are currently "open".
     *   quoteStack: for each interpolation, the quote-char and quote-run length
     *   to return to when '}' closes the interpolation. */
    int  depth;
    int  quote_chars[16];
    int  quote_runs[16];
    /* brace tracking per active interp: when braces_open[depth]==0, next '}' ends interp */
    int  braces_open[16];
    /* pending token queue for multi-token emissions (str chunks + interp markers) */
    Tok  queued[8];
    int  qhead, qtail;
} Lexer;

void  lex_init(Lexer *L, const char *src, size_t len);
Tok   lex_next(Lexer *L);
const char *tok_name(TokKind k);

/* Skip source bytes until we reach a top-level '=' (assignment), tracking
 * angle-bracket nesting so that `Type<...>` annotations (with arbitrary
 * regex-like content) are passed over without invoking the tokenizer.
 * Used by the parser to handle TypeScript-style `name: Type<...> = expr`
 * declarations. The lexer's position is left immediately before the '='.
 * Returns 1 if a top-level '=' was found, 0 if EOF was hit first. */
int   lex_skip_to_assign(Lexer *L);

#endif
