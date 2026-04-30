/*
* Compile and run with `gcc -o solve solve-nano.c && chmod +x solve && ./solve`
*/

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

uint8_t constants_B_bytes[] = { 0x3d, 0x52, 0xf1, 0xa5, 0x87, 0x73, 0x03, 0x1b, 0x72, 0xf3, 0x6e, 0x3c, 0x85, 0xae, 0x67, 0xbb, 0x67, 0xe6, 0x09, 0x6a, 0x7f, 0x52, 0x0e, 0x51, 0x8c, 0x68, 0x05, 0x9b, 0xab, 0xd9, 0x83, 0x1f };
uint *constants_B = (uint*)constants_B_bytes;

uint8_t constants_A_bytes[] = { 0x11, 0xee, 0xff, 0xc0, 0xde, 0xc0, 0xad, 0x0b, 0x0d, 0xf0, 0xad, 0x8b, 0xce, 0xfa, 0xed, 0xfe };
uint *constants_A = (uint*)constants_A_bytes;

uint8_t encrypted_flag[] = { 0x55, 0xdc, 0xf7, 0x64, 0xda, 0x35, 0xef, 0x9c, 0x95, 0xa0, 0x41, 0x14, 0xd4, 0x9d, 0x2a, 0x9a, 0x7b, 0x61, 0x30, 0x12, 0x5c, 0x91, 0x09, 0xda, 0x7b, 0x2f, 0x73, 0x17, 0x9b, 0xad, 0xff, 0x7a, 0x6b, 0xee, 0x1a, 0x4d, 0xa5, 0xae, 0x14, 0x45 };

uint load_word(uint *param_1) {
  return *param_1;
}

void store_word(uint *param_1,uint param_2) {
  ((char *)param_1)[0] = (char)param_2;
  ((char *)param_1)[1] = (char)(param_2 >> 8);
  ((char *)param_1)[2] = (char)(param_2 >> 0x10);
  ((char *)param_1)[3] = (char)(param_2 >> 0x18);

  return;
}

uint micro_hash(uint param_1,uint8_t param_2) {
  param_2 = param_2 & 0x1f;
  if (param_2 != 0) {
    param_1 = param_1 << param_2 | param_1 >> 0x20 - param_2;
  }

  return param_1;
}

uint micro_hash2(uint param_1,uint8_t param_2) {
  param_2 = param_2 & 0x1f;
  if (param_2 != 0) {
    param_1 = param_1 >> param_2 | param_1 << 0x20 - param_2;
  }

  return param_1;
}

int get_round_key(uint counter) {
  uint G, F;
  
  F = constants_A[counter & 3];
  G = micro_hash(constants_A[counter + 1 & 3],counter + 5);

  return (F ^ G) + (counter + 1) * L'\x9e3779b9';
}


uint block_scrambler(int B,int obscured_const,uint c) {
  uint D, E;
  
  D = micro_hash(B,(c & 7) + 7);
  E = micro_hash2(obscured_const,(c & 3) + 0xb);
  D = (obscured_const + B ^ D) + (E ^ c);
  E = micro_hash(D,0xd);

  return D ^ E;
}


void crypto_func(uint *input) {
  uint round_key, C, A, B, i;
  
  A = load_word(input);
  B = load_word(input + 1);
  for (i = 0; i < 8; i = i + 1) {
    round_key = get_round_key(7-i); // Changed `i` to `7-i` to reverse the roundkey order
    C = block_scrambler(B,round_key,constants_B[7-i]); // Changed `i` to `7-i` to reverse the roundkey order
    C = A ^ C;
    A = B;
    B = C;
  }
  store_word(input, B);
  store_word(input + 1, A);

  return;
}

// Run the reversed feistel network with inverse roundkey order for decrypting instead of encrypting
int main(int argc, char *argv[]) {
  uint j;

  for (j = 0; j < 0x28; j = j + 8) {
    crypto_func((uint *)((long)encrypted_flag + j));
  }

  puts((char*)encrypted_flag);

  return 0;
}
