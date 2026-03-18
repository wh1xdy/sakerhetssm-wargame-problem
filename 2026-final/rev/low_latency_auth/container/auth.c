#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include "xor_filter.h"

#define ARRAY_SIZE 100000

static int hex_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static int parse_hex_byte(const char *src, uint8_t *byte) {
    int hi = hex_value(src[0]);
    int lo = hex_value(src[1]);

    if (hi < 0 || lo < 0) {
        return 0;
    }

    *byte = (uint8_t)((hi << 4) | lo);
    return 1;
}

void mixer(uint16_t *state) {
    for (int round = 0; round < 16; round++) {
        for (int i = 0; i < 8; i++) {
            state[i] = (state[i] + state[(i - 1 + 8) % 8]) & 0xFFFF;
            state[i] ^= (0x9E37 + round) & 0xFFFF;
            state[i] = ((state[i] << 7) | (state[i] >> 9)) & 0xFFFF;
        }
    }
}

uint64_t hash(uint16_t chunk, int pos) {
    uint64_t h = chunk ^ (pos * 0x5bd1e995ULL);
    h ^= h >> 15;
    h *= 0xbf58476d1ce4e5b9ULL;
    h = (h * h) ^ (h >> 32); 
    h *= 0x94d049bb133111ebULL;
    h ^= h >> 31;
    return h;
}

int check_password(const char *hex_input) {
    uint8_t password[16] = {0}; 
    uint16_t chunks[8] = {0};
    
    for (int i = 0; i < 16; i++) {
        if (!parse_hex_byte(&hex_input[i * 2], &password[i])) {
            return 0; 
        }
    }
    
    for (int i = 0; i < 8; i++) {
        chunks[i] = (password[i*2] << 8) | password[i*2 + 1];
    }
    
    mixer(chunks);
    
    uint64_t filter_sum = 0;
    uint64_t expected_fp = 0;
    
    for (int i = 0; i < 8; i++) {
        uint64_t h = hash(chunks[i], i);
        uint32_t idx = (uint32_t)(h & 0xFFFFFFFF) % ARRAY_SIZE;
        uint64_t fp = h; 
        filter_sum ^= FILTER_ARRAY[idx];
        expected_fp ^= fp;
    }
    
    return (filter_sum == expected_fp);
}

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);
    printf("=== Low Latency Edge Node Authentication ===\n");
    printf("Enter 16-byte Password (hex) > ");
    
    char input[35] = {0};
    if (!fgets(input, sizeof(input), stdin)) return 1;

    size_t input_len = strcspn(input, "\n");
    if (input[input_len] == '\n') {
        input[input_len] = '\0';
    }
    
    if (input_len != 32) {
        printf("[-] Invalid length.\n");
        return 1;
    }
    
    if (check_password(input)) {
        printf("\n[+] ACCESS GRANTED.\n");
        printf("[+] FLAG: SSM{<flag>}");
    } else {
        printf("\n[-] ACCESS DENIED.\n");
    }
    return 0;
}
