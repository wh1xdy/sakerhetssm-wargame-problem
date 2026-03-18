#pragma once

#include <stdint.h>
#include <stddef.h>

#define LC3_MEM_SIZE  65536
#define LC3_PC_START  0x3000

/* Condition flag bits */
#define FL_POS 1
#define FL_ZRO 2
#define FL_NEG 4

/* Forward declaration needed so trap_fn can reference LC3. */
typedef struct LC3 LC3;
typedef void (*trap_fn)(LC3 *vm);

struct LC3 {
    uint16_t mem[LC3_MEM_SIZE]; /* LC3 address space, immediately follows vtable  */
    trap_fn  handlers[256];  /* trap dispatch vtable — one entry per 8-bit vector */
    uint16_t reg[8];         /* R0-R7                                              */
    uint16_t pc;
    uint16_t cond;           /* FL_POS | FL_ZRO | FL_NEG                          */
    int      running;
};

void lc3_init(LC3 *vm);
int  lc3_load(LC3 *vm, const char *filename);
int  lc3_load_buf(LC3 *vm, const unsigned char *data, size_t len);
void lc3_run(LC3 *vm);
void lc3_step(LC3 *vm);
