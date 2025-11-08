#!/usr/bin/env python3

import string
import itertools
from libdebug import debugger

OFFSET_CHAR_CORRECT = 0x13c1
FLAG_LEN = 0x1d
#ALPHABET = string.ascii_letters + string.digits + '{}_'
ALPHABET = 'ASD'

class BreakCounter:
    def __init__(self):
        self.count = 0
    
    def breakpoint(self, t, bp):
        self.count += 1

def attempt(flag) -> int:
    dbg = debugger(argv=["../chall"])
    pipe = dbg.run()
    counter = BreakCounter()
    dbg.breakpoint(OFFSET_CHAR_CORRECT, callback=counter.breakpoint, file="binary")
    dbg.cont()
    
    pipe.sendline(flag.encode())
    dbg.wait()
    return counter.count

flag = ''
while len(flag) < FLAG_LEN:
    best = None
    best_count = 0
    for cand_a, cand_b in itertools.product(ALPHABET, repeat=2):
        cand_flag = flag + cand_a + cand_b
        cand_flag = cand_flag.ljust(FLAG_LEN, 'A')
        cand_count = attempt(cand_flag)
        print(f'{flag} {cand_a} {cand_b} {cand_count}')
        if cand_count > best_count:
            best_count = cand_count
            best = cand_a
    flag += best
    print(flag)
