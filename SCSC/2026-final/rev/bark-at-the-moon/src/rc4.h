#include <stdint.h>
#include <stdlib.h>

int RC4(const uint8_t *key, size_t keylen, uint8_t *dst, const uint8_t *src, size_t len);
