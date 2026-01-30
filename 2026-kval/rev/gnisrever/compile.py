import re
import os
import tempfile
import subprocess

if not os.path.exists('./bin'):
    os.makedirs('./bin')

subprocess.run('gcc -o bin/core.S -fPIC -nostdlib -nostartfiles -ffreestanding -fno-asynchronous-unwind-tables -fno-ident -e start -s -S core.c', shell=True)

with open('./bin/core.S', 'r') as f:
    out = ''

    for line in f:
        out += line
        if line.startswith('start:'): break

    instructions = []

    align = '\t.align 16\n'

    for line in f:
        if line.strip().startswith('.size'):
            out += line
            break
        if line.strip().startswith('.'): # label
            instructions += [align, '\tnop\n', line, align, next(f), ]
            continue
        instructions += [align, line]
    instructions += [align]
    out += ''.join(instructions[1:][::-1])
    
    for line in f   :
        out += line

with open('./bin/core_mod.S', 'w') as o:
    o.write(out)

subprocess.run('gcc -c bin/core_mod.S -o bin/core.o', shell=True)
# extract .text using objcopy
subprocess.run('objcopy -O binary --only-section=.text bin/core.o bin/core.bin', shell=True)

with open('./chall_template.c', 'r') as f:
    src = f.read()
src = src.replace('SHELLCODE_PLACEHOLDER', ','.join([f'{b:#02x}' for b in open('./bin/core.bin', 'rb').read()]))

with open('./chall.c', 'w') as f:
    f.write(src)

subprocess.run('gcc ./chall.c -no-pie -o chall', shell=True)