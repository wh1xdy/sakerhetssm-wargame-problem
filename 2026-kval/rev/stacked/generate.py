#!/usr/bin/env python3

# python3 generate.py 'SSM{stack_em_h1gh}' 1337

import random
import sys

FLAG = sys.argv[1]
SEED = sys.argv[2]

random.seed(SEED)

opcodes = {
    'push': 0x01,
    'add': 0x02,
    'sub': 0x03,
    'xor': 0x04,
    'cmp': 0x05,
    'swap': 0x06,
    'halt': 0xff,
}

program = []
for idx, c in enumerate(FLAG[::-1].encode()):
    op = random.choice(['add','sub','xor'])
    operand = random.randint(0,255)
    match op:
        case 'add':
            target = (c + operand) % 256
        case 'sub':
            target = (c - operand) % 256
        case 'xor':
            target = (c ^ operand) % 256

    if idx > 0:
        program.append(opcodes['swap'])

    program.append(opcodes['push'])
    program.append(operand)
    program.append(opcodes[op])
    program.append(opcodes['push'])
    program.append(target)
    program.append(opcodes['cmp'])

    if idx > 0:
        program.append(opcodes['add'])


program.append(opcodes['push'])
program.append(len(FLAG))
program.append(opcodes['cmp'])
program.append(opcodes['halt'])

header = f"""
#include <stdint.h>
#define FLAG_LEN {len(FLAG)}
#define PROGRAM_LEN {len(program)}
extern uint8_t program[PROGRAM_LEN];
"""


with open('program.h', 'w') as fout:
    fout.write(header)

with open('program.c', 'w') as fout:
    fout.write('#include "program.h"\n')
    fout.write(f'uint8_t program[{len(program)}] = {{\n')
    fout.write(', '.join(f'{x}' for x in program) + '\n')
    fout.write('};\n')
