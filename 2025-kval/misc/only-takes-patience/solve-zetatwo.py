#!/usr/bin/env python3

import sys
import time
from ctypes import CDLL

libc = CDLL("libc.so.6")

with open('output.txt', 'r') as fin:
    ciphertext = fin.read().strip()

ciphertext = bytes.fromhex(ciphertext)

timestamp = int(time.time())
for _ in range(10_000_000):
    libc.srand(timestamp)
    cand_plaintext = bytes(x ^ (libc.rand() % 256) for x in ciphertext)

    if cand_plaintext.startswith(b'SSM{'):
        flag = cand_plaintext.decode()
        break

    timestamp -= 1
else:
    print('Failed to find flag')
    sys.exit(1)

print(f'Flag: {flag}')
