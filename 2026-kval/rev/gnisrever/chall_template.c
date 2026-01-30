#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <ucontext.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <stdarg.h>
#include <sys/mman.h>

// Trap flag bit in RFLAGS
#define TF_MASK 0x100

char shellcode[] = {SHELLCODE_PLACEHOLDER};

static void trap_handler(int sig, siginfo_t *si, void *ucontext) {
    (void)sig; (void)si;
    ucontext_t *uc = (ucontext_t *)ucontext;
    greg_t *gregs = uc->uc_mcontext.gregs;
    gregs[REG_RIP] &= ~0xf;
    gregs[REG_RIP] -= 0x10;
}

int main(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_sigaction = trap_handler;
    sa.sa_flags = SA_SIGINFO | SA_RESTART;
    sigemptyset(&sa.sa_mask);

    if (sigaction(SIGTRAP, &sa, NULL) == -1) {
        perror("sigaction");
        return 1;
    }
    
    void* mem = mmap(NULL, sizeof(shellcode),
        PROT_READ | PROT_WRITE | PROT_EXEC,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1, 0);
    if (mem == 0) {
        perror("mmap fail");
        return 1;
    }
    memcpy(mem, shellcode, sizeof(shellcode));
    void* jmp_tgt = mem + sizeof(shellcode) - 4;

    unsigned long flags;
    asm volatile("pushfq\n"
                 "popq %0\n"
                 : "=r"(flags) :: "memory");
    flags |= TF_MASK;
    asm volatile("pushq %0\n"
                "popfq\n"
                "jmp *%1\n"
                 :: "r"(flags), "r"(jmp_tgt) : "memory", "cc");
    return 0;
}