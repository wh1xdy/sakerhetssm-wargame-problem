#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/random.h>

#include "flag.h"

static inline uint64_t rotl(const uint64_t x, int k) {
   return (x << k) | (x >> (64 - k));
}

static uint64_t s[4];

uint64_t next(void) {
   uint32_t result = s[1];
   result *= 5;
   result ^= result << 7;
   result *= 9;

   const uint64_t t = s[1] << 17;

   s[2] ^= s[0];
   s[3] ^= s[1];
   s[1] ^= s[2];
   s[0] ^= s[3];

   s[2] ^= t;

   s[3] = rotl(s[3], 45);

   return result;
}

constexpr uint32_t dots[] = {
    2276344508, 3868698040, 2932233957, 2481846377, 3315139130, 1079154857,
    546696388,  2042452297, 2280531969, 3382719674, 1837261007, 352190692,
    547788629,  2406082427, 1197860883, 376254976,  3001847785, 2516055065,
    2848289332, 471417044,  120242309,  3247271329, 2552421204, 2399516480,
    3128873567, 3305266045, 976269268,  2353587310, 3818595075, 557748429,
    209807908,  459673187};
uint32_t mask(uint32_t inp) {
   uint32_t sum = 0;
   for (size_t i = 0; i < 32; i++) {
      uint32_t bit = (inp >> (31 - i)) & 1;
      sum += bit * dots[i];
   }
   return sum;
}

constexpr size_t len = 40;

void strxor(char *restrict flagout, const char *restrict str) {
   for (size_t i = 0; i < len; i++) {
      flagout[i] ^= str[i];
   }
}

void fill_rand(char *str) {
   for (size_t i = 0; i < len / 4; i++) {
      uint32_t n = next();
      uint32_t r = mask(n);
      str[4 * i] = (r >> 24) & 0xFF;
      str[4 * i + 1] = (r >> 16) & 0xFF;
      str[4 * i + 2] = (r >> 8) & 0xFF;
      str[4 * i + 3] = (r >> 0) & 0xFF;
   }
}

int main() {
   int amount = getrandom(s, 256 / 8, 0);
   assert(amount == 256 / 8);
   assert(strlen(flag) == len);

   for (int i = 0; i < 67; i++) {
      char random[len + 1] = "";
      fill_rand(random);
      strxor(random, flag);
      for (size_t ii = 0; ii < len; ii++) {
         printf("%x ", random[ii] & 0xFF);
      }
      printf("\n");
   }
   return 0;
}
