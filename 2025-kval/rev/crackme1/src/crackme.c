#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "flag.h"

void lcg_crypt(unsigned char* dst, unsigned char* src, size_t len, unsigned long seed, long unsigned m, unsigned long a, unsigned long b, unsigned long bits) {
    unsigned long long state = seed;
    for(size_t i = 0; i < len; i++) {
        state = (state*a + b) % m;
        state &= (1l<<bits)-1;
        dst[i] = src[i] ^ (state&0xFF);
    }
}

int main() {
    printf("Welcome to crackme1\n");
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
    unsigned char decrypted[flag_len];
    memcpy(decrypted, flag_enc, flag_len);

    lcg_crypt(decrypted, decrypted, flag_len, 1339, 1<<23, 65793, 4282663, 32);
    for(size_t i = 0; i < flag_len; i++) {
        decrypted[i] ^= key3[i];
    }

    lcg_crypt(decrypted, decrypted, flag_len, 1338, 1<<31, 214013, 2531011, 32);
    for(size_t i = 0; i < flag_len; i++) {
        decrypted[i] ^= key2[i];
    }

    lcg_crypt(decrypted, decrypted, flag_len, 1337, 1<<31, 1103515245, 12345, 32);
    for(size_t i = 0; i < flag_len; i++) {
        decrypted[i] ^= key1[i];
    }

    if(strlen(input) != flag_len || memcmp(decrypted, input, flag_len) != 0) {
        printf("Wrong!\n");
        return 1;
    } else {
        printf("Correct! Congratulations!\n");
    }

    return 0;
}
