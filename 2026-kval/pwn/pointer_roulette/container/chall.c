#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <sys/random.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>

// writes left
unsigned writes = 1;
uint64_t* ptr = (uint64_t*)&ptr;

void menu() {
    puts("=== Menu ===");
    puts("1. Try your luck with the pointer roulette");
    puts("2. Shoot your shot");
    puts("3. Exit");
    printf("> ");
}

#define bswap(x) (uint64_t*)__builtin_bswap64((uint64_t)x)

void roulette() {
    unsigned bet;
    printf("Enter your bet: ");
    scanf("%u", &bet);

    if (bet > 8) {
        puts("Bet too high!");
        return;
    }
    if (bet == 0) {
        puts("Bet too low!");
        return;
    }

    ptr = bswap(ptr);
    getrandom(&ptr, bet, 0);
    ptr = bswap(ptr);

    printf("Congratulations! You won: %p\n", ptr);
}

void shoot() {
    if (!writes) {
        puts("lol");
        return;
    }

    puts("go ahead buddy...");
    printf("> ");
    uint64_t val;
    scanf("%lu", &val);

    *ptr = val;

    writes--;
}

void lol() {
    char buffer[256];
    puts("tell me smth lil bro");
    //read(0, buffer+32, 256-32);
    read(0, buffer, 256);
    memfrob(buffer, sizeof(buffer));
    puts("encrypted lil bro...");
}

int main(int argc, char** argv) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    
    while (1) {
        menu();
        unsigned option;
        scanf("%u", &option);
        if (option == 1) 
            roulette();
        else if (option == 2)
            shoot();
        else if (option == 67)
            lol();
        else
            exit(0);
    }

    return 0;
}