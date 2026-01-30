#include <syscall.h>
#include <stdbool.h>

#define do_syscall(nr, a, b, c, d, e, f, ...) ({\
    register long rax asm("rax") = (nr);\
    register long rdx asm("rdx") = (c);\
    register long r10 asm("r10") = (d);\
    register long r8 asm("r8") = (e);\
    register long r9 asm("r9") = (f);\
    asm volatile ("syscall\n\t": "=r" (rax):"r" (rdx), "r" (r10), "r" (r8), "r" (r9), "r" (rax), "D" (a), "S" (b):);\
    rax;\
})

#define SYSCALL(nr, ...) do_syscall(nr, __VA_ARGS__, 0, 0, 0, 0, 0, 0)

#define INPLEN 68
int start() {
    char buf[INPLEN];
    char permbuffer[INPLEN];
    char sums[INPLEN] = {128,211,224,223,210,190,198,198,210,230,226,226,223,231,224,198,192,190,200,215,221,208,215,226,224,219,207,205,226,244,217,206,209,215,215,200,194,190,210,232,212,190,178,197,215,211,211,219,232,215,198,205,213,219,191,194,227,226,217,196,200,226,236,216,206,188,184,101};
    char msg[] = {':','d','r','o','w','s','s','a','p',' ','e','h','t',' ','r','e','t','n','E','\n'};
    char permutation[INPLEN] = {66,8,18,7,19,16,22,40,55,49,13,10,53,6,3,26,35,50,32,56,30,54,51,61,52,45,31,34,60,67,4,43,37,15,27,14,33,12,46,64,44,58,42,0,23,5,39,41,25,63,65,21,36,17,59,2,11,57,48,24,20,29,9,28,38,47,1,62};
    SYSCALL(SYS_write, 1, msg, sizeof(msg));
    SYSCALL(SYS_read, 0, buf, INPLEN);

    for (int i = 0; i < INPLEN; i++) {
        permbuffer[i] = buf[permutation[i]];
    }

    bool correct = true;
    for (int i = 0; i < INPLEN; i++) {
        char sum = permbuffer[i];
        if (i < INPLEN - 1) sum += permbuffer[i + 1];
        correct &= (sum == sums[i]);
    }
    
    char win_msg[] = {'!','e','l','a','y','o','r',' ','y','r','o','t','c','i','V','\n'};
    char fail_msg[] = {'!','l','i','a','f',' ','c','i','p','E','\n'};
    SYSCALL(SYS_write, 1, correct ? win_msg : fail_msg, correct ? sizeof(win_msg) : sizeof(fail_msg));
    SYSCALL(SYS_exit, 0);
}