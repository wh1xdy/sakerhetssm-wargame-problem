#include "rc4.h"

#define N 256   // 2^8

void swap(uint8_t *a, uint8_t *b) {
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

static int KSA(uint8_t *S, const uint8_t *key, size_t keylen) {
    int j = 0;
    for(int i = 0; i < N; i++) {
        S[i] = i;
    }

    for(int i = 0; i < N; i++) {
        j = (j + S[i] + key[i % keylen]) % N;
        swap(&S[i], &S[j]);
    }

    return 0;
}

static int PRGA(uint8_t *S, uint8_t *dst, const uint8_t *src, size_t len) {

    int i = 0;
    int j = 0;

    for(size_t n = 0; n < len; n++) {
        i = (i + 1) % N;
        j = (j + S[i]) % N;

        swap(&S[i], &S[j]);
        int rnd = S[(S[i] + S[j]) % N];

        dst[n] = rnd ^ src[n];

    }

    return 0;
}

int RC4(const uint8_t *key, size_t keylen, uint8_t *dst, const uint8_t *src, size_t len) {
    uint8_t S[N];
    KSA(S, key, keylen);
    PRGA(S, dst, src, len);

    return 0;
}
