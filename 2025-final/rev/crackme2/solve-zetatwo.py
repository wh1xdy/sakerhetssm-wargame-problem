#!/usr/bin/env python3

import string
from libdebug import debugger

OFFSET_CHAR_CORRECT = 0x0000132f
ALPHABET = string.ascii_letters + string.digits + '{}_'

class BreakCounter:
    def __init__(self):
        self.count = 0
    
    def breakpoint(self, t, bp):
        self.count += 1

def attempt(flag) -> int:
    dbg = debugger(argv=["./crackme2"])
    pipe = dbg.run()
    counter = BreakCounter()
    dbg.breakpoint(OFFSET_CHAR_CORRECT, callback=counter.breakpoint, file="binary")
    dbg.cont()
    
    pipe.sendline(flag.encode())
    dbg.wait()
    dbg.kill()
    return counter.count

flag = ''
while not flag.endswith('}'):
    best = None
    best_count = 0
    for cand in ALPHABET:
        cand_flag = flag + cand
        cand_count = attempt(cand_flag)
        if cand_count > best_count:
            best_count = cand_count
            best = cand
    flag += best
    print(flag)

print(f'Flag: {flag}')
