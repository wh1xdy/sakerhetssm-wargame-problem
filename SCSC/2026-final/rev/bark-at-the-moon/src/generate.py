#!/usr/bin/env python3

# ./generate.py 1337 'SCSC{Lua_is_v3ry_e4sy_t0_Emb3d}'

import sys
import random
from Crypto.Cipher import ARC4

seed = sys.argv[1]
flag = sys.argv[2]
key = 'Listen in awe and you will hear him'

random.seed(seed)

parameters = random.randbytes(2*len(flag))

target = bytes(((flag.encode()[i] + parameters[2*i]) & 0xFF) ^ parameters[2*i+1] for i in range(len(flag)))

rc4 = ARC4.new(key=key.encode())
target_enc = rc4.encrypt(target)

rc4 = ARC4.new(key=key.encode())
parameters_enc = rc4.encrypt(parameters)

print(f'local N="{len(flag)}"')
print(f'local ENC_PARAMS="{parameters_enc.hex()}"')
print(f'local ENC_TARGET="{target_enc.hex()}"')
