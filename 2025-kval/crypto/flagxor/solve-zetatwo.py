#!/usr/bin/env python3

from pwn import *

HOST = 'localhost'
PORT = 50000

io = remote(HOST, PORT)
io.recvline_contains(b'Please send your 2 secret numbers to encrypt:')

key = (1<<1023)
io.sendline(f'{key}'.encode())
io.sendline(f'{key}'.encode())

part1 = int(io.recvline().decode().strip())
part2 = int(io.recvline().decode().strip())

log.info('Part 1: %d', part1)
log.info('Part 2: %d', part2)

part1b = part1.to_bytes((key.bit_length()+7)//8, 'big')
part2b = part2.to_bytes((key.bit_length()+7)//8, 'big')

flag = (part1b[1:].lstrip(b'\0') + part2b[1:].lstrip(b'\0')).decode()

log.info('Flag: %s', flag)

