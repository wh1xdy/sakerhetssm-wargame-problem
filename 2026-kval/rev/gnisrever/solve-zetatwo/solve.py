#!/usr/bin/env python3

from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CS_OPT_SYNTAX_ATT
from ast import literal_eval

with open('../chall.c', 'r') as fin:
    for line in fin:
        if 'shellcode[]' in line:
            shellcode = bytes(literal_eval(line.split('{', 1)[1].split('}', 1)[0]))

print(shellcode.hex())

md = Cs(CS_ARCH_X86, CS_MODE_64)
md.syntax = CS_OPT_SYNTAX_ATT

current_addr = len(shellcode)-4
while current_addr > 0:

    for i in md.disasm(shellcode[current_addr:current_addr+0x10], 0x1000 + current_addr):
        print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))
        #print(i.size)
        current_addr += i.size
        break

    current_addr &= ~0xf
    current_addr -= 0x10

# A bit of fixing up here of the output, then "gcc -c -o shellcode.o shellcode.S" and open in Binja

# Then, part 2:

target = bytes.fromhex('80d3e0dfd2bec6c6d2e6e2e2dfe7e0c6c0bec8d7ddd0d7e2e0dbcfcde2f4d9ced1d7d7c8c2bed2e8d4beb2c5d7d3d3dbe8d7c6cdd5dbbfc2e3e2d9c4c8e2ecd8cebcb865')
transpose = bytes.fromhex('420812071310162837310d0a3506031a233220381e36333d342d1f223c43042b250f1b0e210c2e402c3a2a0017052729193f411524113b020b393018141d091c262f013e')

values = []
for b in target[::-1]:
    if len(values) > 0:
        b -= values[-1]
    values.append(b)
values = values[::-1]

values = bytes(values[transpose.index(i)] for i in range(len(values)))
print(values.decode())
