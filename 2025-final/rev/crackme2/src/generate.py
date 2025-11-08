#!/usr/bin/env python3

import secrets
import sys

flag_h = sys.argv[1]
flag_c = sys.argv[2]
flag = sys.argv[3]

def encrypt(c: int, i: int) -> int:
    val = c ^ i
    val = (val + 13) & 0xFF
    val = (val ^ 37) & 0xFF
    return val

flag_enc = bytes(encrypt(x, i) for i,x in enumerate(flag.encode()))

with open(flag_h, 'w') as fout:
    fout.write(f'extern const unsigned char flag_enc[{len(flag_enc)}];\n')

flag_hex = ', '.join(f'{x:#04x}' for x in flag_enc)

with open(flag_c, 'w') as fout:
    fout.write('#include "flag.h"\n')
    fout.write(f'const unsigned char flag_enc[{len(flag_enc)}] = {{{flag_hex}}};\n')
