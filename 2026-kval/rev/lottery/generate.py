#!/usr/bin/env python3

# python3 generate.py 'SSM{w0w_that_iz_s0_lucky}' 1337

import sys
import string
import random
import base64

from Crypto.Cipher import ARC4

FLAG = sys.argv[1]
SEED = sys.argv[2]


random.seed(SEED)

alpha = string.ascii_uppercase + string.digits

ticket = ''.join(random.choice(alpha) for _ in range(16))
target = ''.join(random.choice(alpha) for _ in range(16))

key = [x^y for x,y in zip(ticket.encode(), target.encode())]

rc4 = ARC4.new(bytes(ticket.encode()))

encrypted_flag = rc4.encrypt(FLAG.encode())

print(f'Ticket: {ticket}')
print(f'Target: {target}')
print(f'Key: {key}')
print(f'Encrypted Flag: {base64.b64encode(encrypted_flag).decode()}')
