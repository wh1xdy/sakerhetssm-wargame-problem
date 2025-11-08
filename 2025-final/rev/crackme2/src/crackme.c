#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "flag.h"
#include "encrypt.h"

int main() {
    printf("Welcome to crackme2\n");
    char *input = NULL;
    size_t inputlen = 0;
    printf("Please enter the password: ");
    if(-1 == getline(&input, &inputlen, stdin)) {
        free(input);
        fprintf(stderr, "Failed to get input\n");
        return 1;
    }
    input[strcspn(input, "\n")] = 0;

    size_t flag_len = sizeof(unsigned char)*sizeof(flag_enc);
    for(size_t i = 0; i < flag_len; i++) {
        if(encrypt(input[i], i) != flag_enc[i]) {
            printf("Wrong!\n");
            return 1;
        }
    }
    printf("Correct! Congratulations!\n");

    return 0;
}
