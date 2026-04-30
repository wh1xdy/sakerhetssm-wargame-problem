#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

__attribute__((constructor)) static void disable_buffering(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

#define DIE(msg)                                                               \
    do {                                                                       \
        perror(msg);                                                           \
        exit(-1);                                                              \
    } while (0)

#define SEGS (16)

struct JMID2 {
    uint64_t *segments[SEGS];
};

struct DataParser {
    size_t len;
    size_t index;
    uint8_t *buf;
};

static const uint8_t TBL[] = {
    ['0'] = 0,  ['1'] = 1,  ['2'] = 2,  ['3'] = 3,  ['4'] = 4,  ['5'] = 5,
    ['6'] = 6,  ['7'] = 7,  ['8'] = 8,  ['9'] = 9,  ['a'] = 10, ['b'] = 11,
    ['c'] = 12, ['d'] = 13, ['e'] = 14, ['f'] = 15, ['A'] = 10, ['B'] = 11,
    ['C'] = 12, ['D'] = 13, ['E'] = 14, ['F'] = 15};

struct DataParser *DP_FromStdin() {
    struct DataParser *dp = calloc(1, sizeof(struct DataParser));

    uint16_t sz = 0;

    puts("What is the length of your image data: ");
    int err = scanf("%hd", &sz);

    if (err < 1 || err == EOF) DIE("Size not matched");

    char *hex_input = malloc((sz * 2) + 1);
    if (!hex_input) DIE("Memory allocation failed for hex string");

    uint8_t *data = malloc(sz);
    if (!data) DIE("Memory allocation failed for data buffer");
    dp->buf = data;
    dp->len = sz;

    printf("Enter %d hex characters: ", sz * 2);

    char format[32];
    snprintf(&format[0], 31, "%%%ds", sz * 2);
    if (scanf(format, hex_input) < 1) DIE("Failed to read hex string");

    for (short i = 0; i < sz; i++) {
        uint8_t hi = TBL[(unsigned char)hex_input[i * 2]];
        uint8_t lo = TBL[(unsigned char)hex_input[i * 2 + 1]];
        dp->buf[i] = (hi << 4) | lo;
    }

    free(hex_input);

    return dp;
}

struct JMID2 *ParseJMID2(struct DataParser *dp) {
    enum OP {
        OP_CPY = 0x0,
        OP_DEL = 0x1,
        OP_XOR = 0x2,
        OP_NOR = 0x3,
        OP_AND = 0x4,
        OP_ROT = 0x5,
    };

    struct JMID2 *jm = calloc(1, sizeof(struct JMID2));

    while (dp->index < dp->len) {
        switch (dp->buf[dp->index++]) {
        case OP_CPY: {
            // <1 byte opcode> <1 byte segment index> <8 bytes segment data>

            if ((dp->index + 9) > dp->len) DIE("CPY: Not enough data in buf");

            uint8_t idx = dp->buf[dp->index++];
            if (idx >= SEGS) DIE("CPY: Invalid segment index");

            uint64_t *buf = malloc(sizeof(uint64_t));
            memcpy(buf, &dp->buf[dp->index], 8);
            dp->index += 8;

            jm->segments[idx] = buf;
            break;
        }
        case OP_DEL: {
            // <1 byte segment index>
            if ((dp->index >= dp->len)) DIE("DEL: Not enough data in buf");

            uint8_t idx = dp->buf[dp->index++];
            if (idx >= SEGS) DIE("DEL: Invalid segment index");

            free(jm->segments[idx]);

            break;
        }

        case OP_XOR: {
            // <1 byte segment index C> <1 byte segment index A> <1 byte segment index B>
            // C = A xor B
            if ((dp->index + 3 > dp->len)) DIE("XOR: Not enough data in buf");

            uint8_t idxc = dp->buf[dp->index++];
            if (idxc >= SEGS) DIE("XOR: Invalid segment index C");
            uint8_t idxa = dp->buf[dp->index++];
            if (idxa >= SEGS) DIE("XOR: Invalid segment index A");
            uint8_t idxb = dp->buf[dp->index++];
            if (idxb >= SEGS) DIE("XOR: Invalid segment index B");

            if (!jm->segments[idxa] || !jm->segments[idxb]) DIE("XOR: Segments A||B are null");

            uint64_t a = *jm->segments[idxa];
            uint64_t b = *jm->segments[idxb];

            if (!jm->segments[idxc]) jm->segments[idxc] = malloc(sizeof(uint64_t));
            if (!jm->segments[idxc]) DIE("XOR: Failed memory allocation.");

            *jm->segments[idxc] = a ^ b;

            break;
        }

        case OP_NOR: {
            // <1 byte segment index C> <1 byte segment index A> <1 byte segment index B>
            // C = A nor B
            if ((dp->index + 3 > dp->len)) DIE("NOR: Not enough data in buf");

            uint8_t idxc = dp->buf[dp->index++];
            if (idxc >= SEGS) DIE("NOR: Invalid segment index C");
            uint8_t idxa = dp->buf[dp->index++];
            if (idxa >= SEGS) DIE("NOR: Invalid segment index A");
            uint8_t idxb = dp->buf[dp->index++];
            if (idxb >= SEGS) DIE("NOR: Invalid segment index B");

            if (!jm->segments[idxa] || !jm->segments[idxb]) DIE("NOR: Segments A||B are null");

            uint64_t a = *jm->segments[idxa];
            uint64_t b = *jm->segments[idxb];

            if (!jm->segments[idxc]) jm->segments[idxc] = malloc(sizeof(uint64_t));
            if (!jm->segments[idxc]) DIE("NOR: Failed memory allocation.");

            *jm->segments[idxc] = ~(a | b);

            break;
        }

        case OP_AND: {
            // <1 byte segment index C> <1 byte segment index A> <1 byte segment index B>
            // C = A and B
            if ((dp->index + 3 > dp->len)) DIE("AND: Not enough data in buf");

            uint8_t idxc = dp->buf[dp->index++];
            if (idxc >= SEGS) DIE("AND: Invalid segment index C");
            uint8_t idxa = dp->buf[dp->index++];
            if (idxa >= SEGS) DIE("AND: Invalid segment index A");
            uint8_t idxb = dp->buf[dp->index++];
            if (idxb >= SEGS) DIE("AND: Invalid segment index B");

            if (!jm->segments[idxa] || !jm->segments[idxb]) DIE("AND: Segments A||B are null");

            uint64_t a = *jm->segments[idxa];
            uint64_t b = *jm->segments[idxb];

            if (!jm->segments[idxc]) jm->segments[idxc] = malloc(sizeof(uint64_t));
            if (!jm->segments[idxc]) DIE("AND: Failed memory allocation.");

            *jm->segments[idxc] = a & b;

            break;
        }

        case OP_ROT: {
            // <1 byte segment index B> <1 byte segment index A> <1 byte segment index amount>
            // B = A rot amount
            if ((dp->index + 3 > dp->len)) DIE("ROT: Not enough data in buf");

            uint8_t idxb = dp->buf[dp->index++];
            if (idxb >= SEGS) DIE("ROT: Invalid segment index B");
            uint8_t idxa = dp->buf[dp->index++];
            if (idxa >= SEGS) DIE("ROT: Invalid segment index A");
            uint8_t amnt = dp->buf[dp->index++];

            if (!jm->segments[idxa]) DIE("ROT: Segment A is null");

            uint64_t a = *jm->segments[idxa];

            if (!jm->segments[idxb]) jm->segments[idxb] = malloc(sizeof(uint64_t));
            if (!jm->segments[idxb]) DIE("AND: Failed memory allocation.");

            *jm->segments[idxb] = (a >> (amnt & 63)) | (a << (64 - (amnt & 63)));

            break;
        }

        default:
            DIE("Invalid parsing of JMID2 data");
        }
    };

    return jm;
}

void print_segment(uint64_t v) {
    // treat v as 8 rows of 8 bits, MSB of each byte = leftmost pixel
    // each char covers 1 col x 2 rows -> 8 chars wide, 4 rows tall
    // ' '=both off, '▀'=top only, '▄'=bottom only, '█'=both on
    fputs("\xe2\x94\x8c", stdout); // ┌
    for (int i = 0; i < 8; i++) fputs("\xe2\x94\x80", stdout); // ─
    fputs("\xe2\x94\x90\n", stdout); // ┐
    for (int row = 0; row < 8; row += 2) {
        uint8_t top = (v >> (56 - row * 8)) & 0xFF;
        uint8_t bot = (v >> (56 - (row + 1) * 8)) & 0xFF;
        fputs("\xe2\x94\x82", stdout); // │
        for (int col = 0; col < 8; col++) {
            int t = (top >> (7 - col)) & 1;
            int b = (bot >> (7 - col)) & 1;
            if      (!t && !b) putchar(' ');
            else if ( t && !b) fputs("\xe2\x96\x80", stdout); // ▀ U+2580
            else if (!t &&  b) fputs("\xe2\x96\x84", stdout); // ▄ U+2584
            else               fputs("\xe2\x96\x88", stdout); // █ U+2588
        }
        fputs("\xe2\x94\x82\n", stdout); // │
    }
    fputs("\xe2\x94\x94", stdout); // └
    for (int i = 0; i < 8; i++) fputs("\xe2\x94\x80", stdout); // ─
    fputs("\xe2\x94\x98\n", stdout); // ┘
}

int main(void) {
    struct DataParser *dp = DP_FromStdin();
    struct JMID2* jm = ParseJMID2(dp);

    for (int i = 0; i < SEGS; i++) {
        if (jm->segments[i]) {
            printf("Segment %d (%p):\n", i, jm->segments[i][0]);
            print_segment(jm->segments[i][0]);
        }
    }
}
