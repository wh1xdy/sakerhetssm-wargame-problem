#!/usr/bin/env python3

'''
@author grocid / MSAB
@category crypto
@description 
I've devised a new RNG, which I call DUAL_LCG_DBRG
It's keyed, so even by knowing the state of the
RNG, it is not predictable. By employing massive
amounts of non-linearity via low-level bit operations
I have made it both secure and highly efficient on 
low-power devices.
'''

import hashlib
import random
from flag import *

# nothing up my sleeve, promise
p = 340282366920938463463374607431768211507
a = 168725966554698209319210171394357022731
k = 237893247894378324897243897423987423791

nbits = 128 # NIST might want to increase this but what the hay
secret = random.randint(0, p) # pick a random key for test
state = 0

def H(x):
    # we need a proper masking function
    return int(hashlib.sha256(str(x).encode('ascii')).hexdigest(), 16) & 1

def randbit():
    global state
    window = nbits // 2
    n = (state + k) % p
    lo = n % (1 << window)
    n = (a * state - k) % p
    hi = n // (1 << window)
    state ^= (hi << window | lo)
    # ain't gettin' no secrets from here
    return H(state + secret)

state = int(input("state: "), 0)
observation = [randbit() for _ in range(100)]
print(observation)

for _ in range(100):
    assert int(input("> "), 0) == randbit()

print(flag)
