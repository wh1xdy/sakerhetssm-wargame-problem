#!/usr/bin/env python3

from typing import List

from capstone import *
from libdebug import debugger

d = debugger("./paket")

pipes = d.run()
pipes.sendline(20*b'A')

md = Cs(CS_ARCH_X86, CS_MODE_64)

seen = set()

compares: List[str] = []
while not d.dead:
    rip = d.regs.rip
    if rip not in seen:
        seen.add(rip)
        ins = next(md.disasm(d.memory[rip, 0x10], rip, count=1))
        print("0x%x:\t%s\t%s" %(ins.address, ins.mnemonic, ins.op_str))
        if ins.mnemonic == 'cmp':
            compares.append(ins.op_str)

    d.si()

flag = bytes(int(x.split(',', 1)[1], 16) for x in compares[:-1]).decode()
print(f'Flag: {flag}')
