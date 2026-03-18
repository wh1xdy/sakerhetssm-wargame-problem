#!/usr/bin/env python3

"""
./generator.py 1337 'SSM{0ld_skooL_fuN}'
Sequence: [1, 2, 1, 1, 1, 3, 3, 3, 1, 1, 0, 0, 0, 2, 2, 2, 3, 1, 2, 2, 1, 0, 1, 1, 3, 0, 1, 0, 2, 2, 3, 1]
Multiplier: 8686284858880037379
Inverse: -3007687244015163221
Target: 8284347774897715207
Key: 50c628f3fa95c4e1857bd377ef0a0d4cc69eef50
Ciphertext: [214, 84, 149, 167, 182, 77, 111, 159, 150, 52, 192, 180, 88, 249, 81, 230, 85, 39]
"""

import sys
import random
import struct
import hashlib

from Crypto.Cipher import ARC4

MASK_64 = (1 << 64) - 1
SEQUENCE_LENGTH = 32

DIRECTIONS = ['R', 'U', 'L', 'D']

seed = sys.argv[1]
flag = sys.argv[2]

random.seed(seed)

multiplier = random.randrange(0, 1 << 64)
while multiplier % 2 == 0:
    multiplier //= 2

sequence = random.choices([0, 1, 2, 3], k=SEQUENCE_LENGTH)

print(f"Sequence: {sequence}")
print(f"Moves: {', '.join(DIRECTIONS[x] for x in sequence)}")
print(f"Multiplier: {multiplier}")
inverse = pow(multiplier, -1, 1 << 64)
inverse = struct.unpack('<q', struct.pack('<Q', inverse))[0]
print(f"Inverse: {inverse}")

sequence_hash = 0
for x in sequence:
    sequence_hash <<= 2
    sequence_hash |= x
    sequence_hash &= MASK_64

target = (sequence_hash * multiplier) & MASK_64
target = struct.unpack('<q', struct.pack('<Q', target))[0]
print(f"Target: {target}")

key = hashlib.sha1(bytes(sequence)).hexdigest().lower()
print(f'Key: {key}')
rc4 = ARC4.new(key=key.encode())
ciphertext = rc4.encrypt(flag.encode())
print(f'Ciphertext: {list(ciphertext)}')
