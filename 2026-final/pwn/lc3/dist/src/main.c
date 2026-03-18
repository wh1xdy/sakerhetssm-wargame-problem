#include "emu.h"
#include "2048_obj.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/* Maximum bytes accepted for a user-supplied program. */
#define MAX_PROG_BYTES 8192

static int hex_digit(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

/*
 * Read a hex string from stdin and load it as an LC-3 .obj program.
 * Expected input: even-length hex string followed by newline,
 * e.g. "3000200f...".
 */
static int load_hex_program(LC3 *vm)
{
    static char hexbuf[MAX_PROG_BYTES * 2 + 2];
    static unsigned char progbuf[MAX_PROG_BYTES];

    printf("Enter program as hex: ");
    fflush(stdout);

    if (!fgets(hexbuf, sizeof(hexbuf), stdin)) {
        fprintf(stderr, "Read error\n");
        return -1;
    }

    /* Strip trailing newline/whitespace. */
    size_t hexlen = strlen(hexbuf);
    while (hexlen > 0 && isspace((unsigned char)hexbuf[hexlen - 1]))
        hexbuf[--hexlen] = '\0';

    if (hexlen == 0 || hexlen % 2 != 0) {
        fprintf(stderr, "Invalid hex input (must be even length)\n");
        return -1;
    }

    /* Decode hex pairs into bytes. */
    size_t nbytes = hexlen / 2;
    for (size_t i = 0; i < nbytes; i++) {
        int hi = hex_digit(hexbuf[i * 2]);
        int lo = hex_digit(hexbuf[i * 2 + 1]);
        if (hi < 0 || lo < 0) {
            fprintf(stderr, "Invalid hex character\n");
            return -1;
        }
        progbuf[i] = (unsigned char)((hi << 4) | lo);
    }

    return lc3_load_buf(vm, progbuf, nbytes);
}

static LC3 vm __attribute__((section(".vmdata,\"aw\",@nobits#")));

int main(void)
{
    printf("LC-3 Emulator\n");
    printf("  1. Play 2048\n");
    printf("  2. Load custom program (hex)\n");
    printf("> ");
    fflush(stdout);

    char choice[4];
    if (!fgets(choice, sizeof(choice), stdin)) {
        fprintf(stderr, "Read error\n");
        return 1;
    }

    lc3_init(&vm);

    switch (choice[0]) {
    case '1':
        if (lc3_load_buf(&vm, game_2048, game_2048_len) < 0)
            return 1;
        break;
    case '2':
        if (load_hex_program(&vm) < 0)
            return 1;
        break;
    default:
        fprintf(stderr, "Invalid choice\n");
        return 1;
    }

    lc3_run(&vm);
    return 0;
}
