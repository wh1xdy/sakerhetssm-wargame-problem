#!/usr/bin/env python3

from pwn import *
from hashlib import sha256
from Crypto.Util import number


def rotl256(inp, amount):
    return (inp << amount | inp >> (256 - amount)) & ((1 << 256) - 1)


def create_mask(n):
    n2 = n**2

    def mask(inp):
        inp = rotl256(inp, 57)
        inp ^= 0x3d90103675a7d8d5d6663c9d5efa829eabe98a276f2ad183d4b8e24c98e3d525
        inp = (inp * n2) & ((1 << 256) - 1)
        inp = rotl256(inp, 103)
        return number.long_to_bytes(inp)

    return mask


HOST = 'localhost'
PORT = 50000

io = remote(HOST, PORT)
io.recvuntil(b'MULTIPLIER: ')
multiplier = int(io.recvline().decode().strip())
log.info('Multiplier: %d', multiplier)

mask = create_mask(multiplier)

SHIFT = 203
SEARCH = 1 << 28  # ceil((256-203)/2) + margin

seen = set()
with log.progress('Searching for collision') as p:
    for cand in range(SEARCH):  # ceil((256-SHIFT)/2)
        if (cand & 0xffff) == 0:
            p.status('%#x', cand)
        m = mask(cand)
        h = int(sha256(b"GIFFEL-" + m).hexdigest(), 16) >> SHIFT

        if h in seen:
            inp1 = cand
            collision_hash = h
            p.success('found %#x => %#x', inp1, collision_hash)
            break

        seen.add(h)
    else:
        p.failure('failed')
        sys.exit(1)

with log.progress('Recover inp2') as p:
    for cand in range(inp1):
        if (cand & 0xffff) == 0:
            p.status('%#x', cand)
        m = mask(cand)
        h = int(sha256(b"GIFFEL-" + m).hexdigest(), 16) >> SHIFT
        if h == collision_hash:
            inp2 = cand
            p.success('found %#x, %#x => %#x', inp1, inp2, collision_hash)
            break

log.info('Inputs: %#x, %#x', inp1, inp2)

m1 = mask(inp1)
h1 = int(sha256(b"GIFFEL-" + m1).hexdigest(), 16) >> SHIFT
m2 = mask(inp2)
h2 = int(sha256(b"GIFFEL-" + m2).hexdigest(), 16) >> SHIFT
log.info('Validate: %s', h1 == h2)

io.recvuntil(b'> ')
io.sendline(f'{inp1:x}'.encode())
io.recvuntil(b'> ')
io.sendline(f'{inp2:x}'.encode())
io.interactive()
