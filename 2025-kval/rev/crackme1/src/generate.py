#!/usr/bin/env python3

import secrets
import sys

flag_h = sys.argv[1]
flag_c = sys.argv[2]
flag = sys.argv[3]

class LCG:
    def __init__(self, state, m, a, b, bits = 32):
        self.state = state
        self.m = m
        self.a = a
        self.b = b
        self.bits = bits

    def next(self) -> int:
        new_state = (self.state*self.a + self.b) % self.m
        new_state &= (1<<self.bits)-1
        self.state = new_state
        #print(f'state: {self.state:#x}')
        return self.state

flag_bytes0 = flag.encode()

key1 = secrets.token_bytes(len(flag))
flag_bytes1a = bytes(x ^ y for x,y in zip(flag_bytes0, key1))
prng1 = LCG(1337, 1<<31, 1103515245, 12345)
flag_bytes1b = bytes(x ^ (prng1.next() & 0xFF) for x in flag_bytes1a)

key2 = secrets.token_bytes(len(flag))
flag_bytes2a = bytes(x ^ y for x,y in zip(flag_bytes1b, key2))
prng2 = LCG(1338, 1<<31, 214013, 2531011)
flag_bytes2b = bytes(x ^ (prng2.next() & 0xFF) for x in flag_bytes2a)

key3 = secrets.token_bytes(len(flag))
flag_bytes3a = bytes(x ^ y for x,y in zip(flag_bytes2b, key3))
prng3 = LCG(1339, 1<<23, 65793, 4282663)
flag_bytes3b = bytes(x ^ (prng3.next() & 0xFF) for x in flag_bytes3a)

with open(flag_h, 'w') as fout:
    fout.write(f'extern const unsigned char flag_enc[{len(flag_bytes3b)}];\n')
    fout.write(f'extern const unsigned char key1[{len(key1)}];\n')
    fout.write(f'extern const unsigned char key2[{len(key2)}];\n')
    fout.write(f'extern const unsigned char key3[{len(key3)}];\n')

flag_hex = ', '.join(f'{x:#04x}' for x in flag_bytes3b)
key1_hex = ', '.join(f'{x:#04x}' for x in key1)
key2_hex = ', '.join(f'{x:#04x}' for x in key2)
key3_hex = ', '.join(f'{x:#04x}' for x in key3)

with open(flag_c, 'w') as fout:
    fout.write('#include "flag.h"\n')
    fout.write(f'const unsigned char flag_enc[{len(flag_bytes3b)}] = {{ {flag_hex} }};\n')
    fout.write(f'const unsigned char key1[{len(key1)}] = {{ {key1_hex} }};\n')
    fout.write(f'const unsigned char key2[{len(key2)}] = {{ {key2_hex} }};\n')
    fout.write(f'const unsigned char key3[{len(key3)}] = {{ {key3_hex} }};\n')
