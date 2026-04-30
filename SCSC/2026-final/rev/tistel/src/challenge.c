#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "target.h"

#define ROUNDS 8

static uint32_t rol32(uint32_t x, unsigned r) {
	r &= 31u;
	if (r == 0) {
		return x;
	}
	return (x << r) | (x >> (32u - r));
}

static uint32_t ror32(uint32_t x, unsigned r) {
	r &= 31u;
	if (r == 0) {
		return x;
	}
	return (x >> r) | (x << (32u - r));
}

static uint32_t load_le32(const uint8_t *p) {
	return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) |
	       ((uint32_t)p[3] << 24);
}

static void store_le32(uint8_t *p, uint32_t v) {
	p[0] = (uint8_t)(v);
	p[1] = (uint8_t)(v >> 8);
	p[2] = (uint8_t)(v >> 16);
	p[3] = (uint8_t)(v >> 24);
}

static __attribute__((noinline)) uint32_t subkey(unsigned round) {
	uint32_t k = MASTER_KEY[round & 3u];
	k ^= rol32(MASTER_KEY[(round + 1u) & 3u], (unsigned)(5u + round));
	k += (uint32_t)(0x9e3779b9u * (round + 1u));
	return k;
}

static __attribute__((noinline)) uint32_t round_f(uint32_t r, uint32_t k, uint32_t c) {
	uint32_t x = r + k;
	x ^= rol32(r, (unsigned)(7u + (c & 7u)));
	x += (c ^ ror32(k, (unsigned)(11u + (c & 3u))));
	x ^= rol32(x, 13u);
	return x;
}

static void feistel_encrypt_block(uint8_t block[8]) {
	uint32_t l = load_le32(block);
	uint32_t r = load_le32(block + 4);

	for (unsigned i = 0; i < ROUNDS; i++) {
		uint32_t k = subkey(i);
		uint32_t f = round_f(r, k, ROUND_CONSTS[i]);
		uint32_t new_l = r;
		uint32_t new_r = l ^ f;
		l = new_l;
		r = new_r;
	}

	store_le32(block, r);
	store_le32(block + 4, l);
}

static int check_flag(const char *s) {
	const char *prefix = "SCSC{";
	size_t len = strlen(s);

	if (len == 0) {
		return 0;
	}
	if (len != FLAG_LEN) {
		return 0;
	}
	if (strncmp(s, prefix, strlen(prefix)) != 0) {
		return 0;
	}
	if (s[len - 1] != '}') {
		return 0;
	}

	uint8_t buf[TARGET_LEN];
	memcpy(buf, s, len);

	uint8_t pad = (uint8_t)(8u - (len % 8u));
	if (pad == 0) {
		pad = 8;
	}
	for (size_t i = 0; i < (size_t)pad; i++) {
		buf[len + i] = pad;
	}

	for (size_t off = 0; off < TARGET_LEN; off += 8) {
		feistel_encrypt_block(buf + off);
	}

	uint8_t diff = 0;
	for (size_t i = 0; i < TARGET_LEN; i++) {
		diff |= (uint8_t)(buf[i] ^ TARGET[i]);
	}
	return diff == 0;
}

static void strip_newline(char *s) {
	for (size_t i = 0; s[i]; i++) {
		if (s[i] == '\n' || s[i] == '\r') {
			s[i] = '\0';
			return;
		}
	}
}

int main(void) {
	char in[256];

	if (fgets(in, sizeof(in), stdin) == NULL) {
		return 1;
	}
	strip_newline(in);

	if (check_flag(in)) {
		puts("Correct!");
		return 0;
	}
	puts("Wrong.");
	return 0;
}
