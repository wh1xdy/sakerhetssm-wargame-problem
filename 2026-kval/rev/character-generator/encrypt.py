#!/usr/bin/env python3

# python3 encrypt.py 'SSM{an_4bsolut3_h3r0}' 1337
# echo "Sarah Kerrigan" | python3 character.py

import hashlib
import hmac
import itertools
import random
import sys

FLAG = sys.argv[1]
SEED = sys.argv[2]

random.seed(SEED)

def crypt(key, ciphertext):
    result = b""
    for idx, block in enumerate(itertools.batched(ciphertext, 16)):
        block = bytes(block).ljust(16, b"\0")
        kblock = hmac.digest(key, idx.to_bytes(8, "big"), hashlib.sha256)
        result += bytes(a ^ b for a, b in zip(block, kblock))
    return result[: len(ciphertext)]

name = 'Sarah Kerrigan'

name_bits = int.from_bytes(name.encode(), 'little')
idx = 0
while name_bits > 0:
    if name_bits & 1:
        #print(idx + 16)
        print('print("CODE")')
    else:
        print('')
    name_bits >>= 1
    idx += 1

print(crypt(name.encode(), FLAG.encode()).hex())
