#include "emu.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <termios.h>

/* -------------------------------------------------------------------------
 * Constants
 * ---------------------------------------------------------------------- */

/* Opcodes */
enum {
    OP_BR   = 0x0,
    OP_ADD  = 0x1,
    OP_LD   = 0x2,
    OP_ST   = 0x3,
    OP_JSR  = 0x4,
    OP_AND  = 0x5,
    OP_LDR  = 0x6,
    OP_STR  = 0x7,
    OP_RTI  = 0x8,
    OP_NOT  = 0x9,
    OP_LDI  = 0xA,
    OP_STI  = 0xB,
    OP_JMP  = 0xC,
    OP_RES  = 0xD,
    OP_LEA  = 0xE,
    OP_TRAP = 0xF,
};

/* Trap vector codes */
#define TRAP_GETC  0x20   /* read char from keyboard, no echo     */
#define TRAP_OUT   0x21   /* output char in R0[7:0]               */
#define TRAP_PUTS  0x22   /* output null-terminated word string   */
#define TRAP_IN    0x23   /* prompt + read char, echo it          */
#define TRAP_PUTSP 0x24   /* output packed byte string            */
#define TRAP_HALT  0x25   /* halt execution                       */

/* Memory-mapped I/O */
#define MR_KBSR  0xFE00   /* keyboard status register (bit15=ready) */
#define MR_KBDR  0xFE02   /* keyboard data register                 */

/* -------------------------------------------------------------------------
 * Terminal setup — disable canonical mode and echo when stdin is a TTY.
 * Guarded by isatty() so it is silently skipped over a socket.
 * ---------------------------------------------------------------------- */

static struct termios g_saved_termios;

static void restore_terminal(void)
{
    tcsetattr(STDIN_FILENO, TCSANOW, &g_saved_termios);
}

static void setup_terminal(void)
{
    if (!isatty(STDIN_FILENO))
        return;
    tcgetattr(STDIN_FILENO, &g_saved_termios);
    atexit(restore_terminal);
    struct termios raw = g_saved_termios;
    raw.c_lflag &= (tcflag_t)~(ICANON | ECHO);
    raw.c_cc[VMIN]  = 1;
    raw.c_cc[VTIME] = 0;
    tcsetattr(STDIN_FILENO, TCSANOW, &raw);
}

/* -------------------------------------------------------------------------
 * I/O helpers — bypass stdio buffering entirely
 * ---------------------------------------------------------------------- */

static int read_byte(void)
{
    unsigned char c;
    if (read(STDIN_FILENO, &c, 1) != 1)
        return EOF;
    return c;
}

/* -------------------------------------------------------------------------
 * Helpers
 * ---------------------------------------------------------------------- */

/* Sign-extend an `bits`-wide value to 16 bits. */
static inline uint16_t sign_extend(uint16_t x, int bits)
{
    if ((x >> (bits - 1)) & 1)
        x |= (uint16_t)(~0u << bits);
    return x;
}

/* Update condition codes after writing register `r`. */
static inline void update_flags(LC3 *vm, uint16_t r)
{
    if      (vm->reg[r] == 0)     vm->cond = FL_ZRO;
    else if (vm->reg[r] >> 15)    vm->cond = FL_NEG;
    else                          vm->cond = FL_POS;
}

/* -------------------------------------------------------------------------
 * Memory access (intercepts KBSR/KBDR for memory-mapped keyboard)
 * ---------------------------------------------------------------------- */

static uint16_t mem_read(LC3 *vm, uint16_t addr)
{
    if (addr == MR_KBSR) {
        /* Over a socket there is no TTY to poll non-blocking.
           Block until a byte arrives, then mark it ready. */
        vm->mem[MR_KBDR] = (uint16_t)read_byte();
        vm->mem[MR_KBSR] = 0x8000;
    }
    return vm->mem[addr];
}

static void mem_write(LC3 *vm, uint16_t addr, uint16_t val)
{
    vm->mem[addr] = val;
}

/* -------------------------------------------------------------------------
 * Trap handlers — one function per vector, stored in vm->handlers[]
 * ---------------------------------------------------------------------- */

static void trap_getc(LC3 *vm)
{
    vm->reg[0] = (uint16_t)read_byte();
}

static void trap_out(LC3 *vm)
{
    putchar((char)(vm->reg[0] & 0xFF));
    fflush(stdout);
}

static void trap_puts(LC3 *vm)
{
    /* R0 = starting address; each word holds one character. */
    uint16_t addr = vm->reg[0];
    while (vm->mem[addr])
        putchar((char)(vm->mem[addr++] & 0xFF));
    fflush(stdout);
}

static void trap_in(LC3 *vm)
{
    printf("> ");
    fflush(stdout);
    int c = read_byte();
    putchar(c);
    fflush(stdout);
    vm->reg[0] = (uint16_t)c;
}

static void trap_putsp(LC3 *vm)
{
    /* Packed string: low byte first, then high byte; stop at null. */
    uint16_t addr = vm->reg[0];
    uint16_t word;
    while ((word = vm->mem[addr++]) != 0) {
        char lo = (char)(word & 0xFF);
        char hi = (char)(word >> 8);
        putchar(lo);
        if (hi) putchar(hi);
    }
    fflush(stdout);
}

static void trap_halt(LC3 *vm)
{
    puts("\n--- HALT ---");
    vm->running = 0;
}

/* -------------------------------------------------------------------------
 * Single instruction step
 * ---------------------------------------------------------------------- */

void lc3_step(LC3 *vm)
{
    /* Fetch: read instruction and advance PC before decode. */
    uint16_t instr = mem_read(vm, vm->pc++);
    uint16_t op    = instr >> 12;

    switch (op) {

    /* ------------------------------------------------------------------
     * BR  — branch if condition flags match
     * [15:12]=0000 [11]=n [10]=z [9]=p [8:0]=PCoffset9
     * ---------------------------------------------------------------- */
    case OP_BR: {
        uint16_t nzp    = (instr >> 9) & 0x7;
        uint16_t offset = sign_extend(instr & 0x1FF, 9);
        if (nzp & vm->cond)
            vm->pc += offset;
        break;
    }

    /* ------------------------------------------------------------------
     * ADD — DR = SR1 + SR2  |  DR = SR1 + imm5
     * [15:12]=0001 [11:9]=DR [8:6]=SR1 [5]=mode
     *   mode=0: [4:3]=00 [2:0]=SR2
     *   mode=1: [4:0]=imm5
     * ---------------------------------------------------------------- */
    case OP_ADD: {
        uint16_t dr  = (instr >> 9) & 0x7;
        uint16_t sr1 = (instr >> 6) & 0x7;
        if ((instr >> 5) & 1) {
            vm->reg[dr] = vm->reg[sr1] + sign_extend(instr & 0x1F, 5);
        } else {
            vm->reg[dr] = vm->reg[sr1] + vm->reg[instr & 0x7];
        }
        update_flags(vm, dr);
        break;
    }

    /* ------------------------------------------------------------------
     * LD  — DR = mem[PC + offset9]
     * [15:12]=0010 [11:9]=DR [8:0]=PCoffset9
     * ---------------------------------------------------------------- */
    case OP_LD: {
        uint16_t dr     = (instr >> 9) & 0x7;
        uint16_t offset = sign_extend(instr & 0x1FF, 9);
        vm->reg[dr] = mem_read(vm, vm->pc + offset);
        update_flags(vm, dr);
        break;
    }

    /* ------------------------------------------------------------------
     * ST  — mem[PC + offset9] = SR
     * [15:12]=0011 [11:9]=SR [8:0]=PCoffset9
     * ---------------------------------------------------------------- */
    case OP_ST: {
        uint16_t sr     = (instr >> 9) & 0x7;
        uint16_t offset = sign_extend(instr & 0x1FF, 9);
        mem_write(vm, vm->pc + offset, vm->reg[sr]);
        break;
    }

    /* ------------------------------------------------------------------
     * JSR / JSRR — R7 = PC; PC = PC + offset11  |  PC = BaseR
     * [15:12]=0100 [11]=flag
     *   flag=1 (JSR):  [10:0]=PCoffset11
     *   flag=0 (JSRR): [8:6]=BaseR
     * ---------------------------------------------------------------- */
    case OP_JSR: {
        uint16_t saved = vm->pc;
        if ((instr >> 11) & 1) {
            vm->pc += sign_extend(instr & 0x7FF, 11);
        } else {
            vm->pc = vm->reg[(instr >> 6) & 0x7];
        }
        vm->reg[7] = saved;
        break;
    }

    /* ------------------------------------------------------------------
     * AND — DR = SR1 & SR2  |  DR = SR1 & imm5
     * [15:12]=0101 [11:9]=DR [8:6]=SR1 [5]=mode
     * ---------------------------------------------------------------- */
    case OP_AND: {
        uint16_t dr  = (instr >> 9) & 0x7;
        uint16_t sr1 = (instr >> 6) & 0x7;
        if ((instr >> 5) & 1) {
            vm->reg[dr] = vm->reg[sr1] & sign_extend(instr & 0x1F, 5);
        } else {
            vm->reg[dr] = vm->reg[sr1] & vm->reg[instr & 0x7];
        }
        update_flags(vm, dr);
        break;
    }

    /* ------------------------------------------------------------------
     * LDR — DR = mem[BaseR + offset6]
     * [15:12]=0110 [11:9]=DR [8:6]=BaseR [5:0]=offset6
     * ---------------------------------------------------------------- */
    case OP_LDR: {
        uint16_t dr     = (instr >> 9) & 0x7;
        uint16_t base   = (instr >> 6) & 0x7;
        uint16_t offset = sign_extend(instr & 0x3F, 6);
        vm->reg[dr] = mem_read(vm, vm->reg[base] + offset);
        update_flags(vm, dr);
        break;
    }

    /* ------------------------------------------------------------------
     * STR — mem[BaseR + offset6] = SR
     * [15:12]=0111 [11:9]=SR [8:6]=BaseR [5:0]=offset6
     * ---------------------------------------------------------------- */
    case OP_STR: {
        uint16_t sr     = (instr >> 9) & 0x7;
        uint16_t base   = (instr >> 6) & 0x7;
        uint16_t offset = sign_extend(instr & 0x3F, 6);
        mem_write(vm, vm->reg[base] + offset, vm->reg[sr]);
        break;
    }

    /* ------------------------------------------------------------------
     * RTI — return from interrupt (privilege mode not emulated)
     * ---------------------------------------------------------------- */
    case OP_RTI:
        fprintf(stderr, "RTI is not supported\n");
        vm->running = 0;
        break;

    /* ------------------------------------------------------------------
     * NOT — DR = ~SR
     * [15:12]=1001 [11:9]=DR [8:6]=SR [5:0]=111111
     * ---------------------------------------------------------------- */
    case OP_NOT: {
        uint16_t dr = (instr >> 9) & 0x7;
        uint16_t sr = (instr >> 6) & 0x7;
        vm->reg[dr] = ~vm->reg[sr];
        update_flags(vm, dr);
        break;
    }

    /* ------------------------------------------------------------------
     * LDI — DR = mem[mem[PC + offset9]]
     * [15:12]=1010 [11:9]=DR [8:0]=PCoffset9
     * ---------------------------------------------------------------- */
    case OP_LDI: {
        uint16_t dr     = (instr >> 9) & 0x7;
        uint16_t offset = sign_extend(instr & 0x1FF, 9);
        vm->reg[dr] = mem_read(vm, mem_read(vm, vm->pc + offset));
        update_flags(vm, dr);
        break;
    }

    /* ------------------------------------------------------------------
     * STI — mem[mem[PC + offset9]] = SR
     * [15:12]=1011 [11:9]=SR [8:0]=PCoffset9
     * ---------------------------------------------------------------- */
    case OP_STI: {
        uint16_t sr     = (instr >> 9) & 0x7;
        uint16_t offset = sign_extend(instr & 0x1FF, 9);
        mem_write(vm, mem_read(vm, vm->pc + offset), vm->reg[sr]);
        break;
    }

    /* ------------------------------------------------------------------
     * JMP / RET — PC = BaseR  (RET is JMP R7)
     * [15:12]=1100 [8:6]=BaseR
     * ---------------------------------------------------------------- */
    case OP_JMP:
        vm->pc = vm->reg[(instr >> 6) & 0x7];
        break;

    /* ------------------------------------------------------------------
     * RES — reserved / illegal
     * ---------------------------------------------------------------- */
    case OP_RES:
        fprintf(stderr, "Reserved opcode executed at PC=0x%04X\n",
                vm->pc - 1);
        vm->running = 0;
        break;

    /* ------------------------------------------------------------------
     * LEA — DR = PC + offset9  (condition codes NOT altered per ISA)
     * [15:12]=1110 [11:9]=DR [8:0]=PCoffset9
     * ---------------------------------------------------------------- */
    case OP_LEA: {
        uint16_t dr     = (instr >> 9) & 0x7;
        uint16_t offset = sign_extend(instr & 0x1FF, 9);
        vm->reg[dr] = vm->pc + offset;
        break;
    }

    /* ------------------------------------------------------------------
     * TRAP — invoke OS service routine via handler vtable
     * [15:12]=1111 [11:8]=0000 [7:0]=trapvect8
     * ---------------------------------------------------------------- */
    case OP_TRAP: {
        uint16_t vec = instr & 0xFFF;
        vm->reg[7] = vm->pc;
        if (vm->handlers[vec])
            vm->handlers[vec](vm);
        else {
            fprintf(stderr, "Unknown trap: 0x%03X\n", vec);
            vm->running = 0;
        }
        break;
    }
    }
}

/* -------------------------------------------------------------------------
 * Public API
 * ---------------------------------------------------------------------- */

void lc3_init(LC3 *vm)
{
    memset(vm, 0, sizeof(*vm));
    vm->pc      = LC3_PC_START;
    vm->cond    = FL_ZRO;
    vm->running = 1;

    /* Populate the trap handler vtable for the standard vectors. */
    vm->handlers[TRAP_GETC]  = trap_getc;
    vm->handlers[TRAP_OUT]   = trap_out;
    vm->handlers[TRAP_PUTS]  = trap_puts;
    vm->handlers[TRAP_IN]    = trap_in;
    vm->handlers[TRAP_PUTSP] = trap_putsp;
    vm->handlers[TRAP_HALT]  = trap_halt;
}

/*
 * Load a .obj file into memory.
 * File format: first 16-bit word is origin (big-endian),
 * followed by program words (also big-endian).
 * Returns 0 on success, -1 on error.
 */
int lc3_load(LC3 *vm, const char *filename)
{
    FILE *f = fopen(filename, "rb");
    if (!f) {
        perror(filename);
        return -1;
    }

    /* Read and byte-swap the origin address. */
    uint16_t origin;
    if (fread(&origin, sizeof(origin), 1, f) != 1) {
        fprintf(stderr, "%s: failed to read origin\n", filename);
        fclose(f);
        return -1;
    }
    origin = (uint16_t)((origin >> 8) | (origin << 8));

    /* Read program data directly into the memory array. */
    uint16_t *dst = vm->mem + origin;
    size_t    max = LC3_MEM_SIZE - origin;
    size_t    n   = fread(dst, sizeof(uint16_t), max, f);
    fclose(f);

    /* Byte-swap each word (LC-3 .obj files are big-endian). */
    for (size_t i = 0; i < n; i++)
        dst[i] = (uint16_t)((dst[i] >> 8) | (dst[i] << 8));

    /* Start execution at the origin of the loaded program. */
    vm->pc = origin;
    return 0;
}

/*
 * Load a program from a memory buffer (same big-endian .obj format).
 * Returns 0 on success, -1 on error.
 */
int lc3_load_buf(LC3 *vm, const unsigned char *data, size_t len)
{
    if (len < 2) {
        fprintf(stderr, "Program too short\n");
        return -1;
    }

    /* First two bytes are origin (big-endian). */
    uint16_t origin = ((uint16_t)data[0] << 8) | data[1];

    /* Copy and byte-swap each subsequent word. */
    size_t words = (len - 2) / 2;
    size_t max   = LC3_MEM_SIZE - origin;
    if (words > max) words = max;

    for (size_t i = 0; i < words; i++)
        vm->mem[origin + i] = ((uint16_t)data[2 + i*2] << 8) | data[2 + i*2 + 1];

    vm->pc = origin;
    return 0;
}

/* Run until halted. */
void lc3_run(LC3 *vm)
{
    setup_terminal();
    setvbuf(stdin,  NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    while (vm->running)
        lc3_step(vm);
}
