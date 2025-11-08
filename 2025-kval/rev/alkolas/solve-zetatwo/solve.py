#!/usr/bin/env python3

import struct

TARGET_OFFSET = 0x3020
FLAG_LEN = 0x1d

with open('../chall', 'rb') as fin:
    fin.seek(TARGET_OFFSET)
    target = struct.unpack(f'<{FLAG_LEN}I', fin.read(4*FLAG_LEN))

values = list(target)
for i in range(1000000):
    for j in range(FLAG_LEN):
        jj = FLAG_LEN - j - 1
        values[jj] ^= values[(jj+1)%FLAG_LEN]
        values[jj] *= pow(1337, -1, 1<<32)
        values[jj] &= (1<<32)-1

flag = bytes(values).decode()
print(f'Flag: {flag}')
