#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>

bool is_admin = false;
int functions_run = 0;
int bananas = 0;
bool is_shrimp = false;

void print_flag() {
    char *flag = getenv("FLAG");
    puts(flag ? flag : "No flag???");
}

void bask_in_the_twilight() {
    puts("The Void claims its own!");
}

void become_shrimp() {
    puts("you are now a shrimp. congrats.");
    if (bananas > 200) bananas = 200;
    is_shrimp = true;
    sleep(1);
    puts("shrimp status: active. life is simple now.");
}

void invent_color() {
    for (int i = 0; i < 8; i++) {
        printf("Performing color research %c\r", "/-\\|"[i % 4]);
        fflush(stdout);
        sleep(1);
    }
    printf("you invented the color \"%s\"\n", rand() % 2 == 0 ? "blurple" : "grongus");
    bananas += rand() % 10;
}

void gamble() {
    int coin = rand() % 100;
    if (is_shrimp) {
        puts("Shrimps are lucky folk.");
        coin = rand() % 7;
    }
    printf("%d\n", coin);
    if (coin == 0) {
        puts("Jackpot!!!");
        bananas += 10000;
    } else if (coin == 101) {
        puts("Even more jackpot!!!!!!");
        is_admin = true;
    } else {
        puts("Damn, life savings gone! But just one more time and you will definitely win!");
        bananas = bananas * 3 / 4;
    }
}

void divorce_chair() {
    printf("you and the chair had a good run.\n");
    sleep(1);
    printf("the chair gets custody of the ottoman.\n");
    sleep(1);
    bananas /= 2;
    printf("you are now single and chairless.\n");
}

void (*admin_functions[])() = {
    print_flag,
    bask_in_the_twilight,
};

void (*functions[])() = {
    become_shrimp,
    invent_color,
    gamble,
    divorce_chair,
};

#define FUNCTION_COUNT 4

int main() {
    puts("Welcome to the very realistic Life Simulator!");
    while (functions_run < 10) {
        printf("//=====================\\\\\n");
        printf("|| is_admin      = %3d ||\n", is_admin);
        printf("|| functions_run = %3d ||\n", functions_run);
        printf("|| bananas       = %3d ||\n", bananas);
        printf("\\\\=====================//\n");
        puts("");
        puts("[0]: become_shrimp");
        puts("[1]: invent_color");
        puts("[2]: gamble");
        puts("[3]: divorce_chair");
        puts("[4]: print_flag");
        puts("[5]: bask_in_the_twilight");
        printf("> ");
        fflush(stdout);

        int n;
        if (scanf("%d", &n) == EOF) break;

        if (n >= FUNCTION_COUNT) {
            if (is_admin) {
                admin_functions[n - FUNCTION_COUNT]();
            } else {
                puts("You must be admin!");
                continue;
            }
        } else {
            functions[n]();
        }
        sleep(1);

        functions_run++;
    }
}
