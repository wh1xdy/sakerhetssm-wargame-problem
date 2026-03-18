#!/usr/bin/env python3

from pwn import *
import re
from typing import Tuple
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

HOST = 'localhost'
PORT = 50000

#io = process(["python3", "src/server.py"])
io = remote(HOST, PORT)


def gcd(a: int, b: int) -> Tuple[int, int]:
    # print(a, b) # DEBUG
    if a == 0 or b == 0:
        return 1, 1
    r = a % b
    d = 1
    while r:
        d += 1
        a = b
        b = r
        r = a % b
    return d, b


def menu(io, choice: int):
    io.recvuntil(b"Choice: ")
    io.sendline(f"{choice}".encode())


def get_flag(io):
    menu(io, 3)
    io.recvuntil(b"Here is the flag: ")
    encrypted_flag = bytes.fromhex(io.recvline().decode().strip())
    return encrypted_flag


def set_exponent(io, exponent: int):
    menu(io, 1)
    io.recvuntil(b"Please enter new exponent: ")
    io.sendline(f"{exponent}".encode())
    line = (
        io.recvline_contains(
            [
                b"Calculated GCD(e, phi) in",
                b"Updated exponent",
                b"Failed to update exponent",
            ]
        )
        .strip()
        .decode()
    )
    iterations = None
    if "Calculated" in line:
        iterations = int(re.search(r"in (\d+) iterations", line)[1])
        io.recvline_contains(
            [b"Updated exponent", b"Failed to update exponent"]
        ).strip().decode()
    return iterations


def get_key_params(io):
    io.recvuntil(b"N: ", drop=True)
    n = int(io.recvline().decode().strip())
    io.recvuntil(b"e: ", drop=True)
    e = int(io.recvline().decode().strip())
    return e, n


e, n = get_key_params(io)
log.info('e=%d', e)
log.info('N=%d', n)
flag = get_flag(io)
_ = set_exponent(io, 0)

candidates = {0, 1}
with log.progress("Leaking bits") as p:
    for i in range(2047):
        p.status("bit %d", i + 1)
        y = 1 << (i + 1)
        iterations = set_exponent(io, y)
        new_candidates = set()
        for candidate in candidates:
            h0 = candidate
            h1 = candidate + (1 << i)
            i0, _ = gcd(h0, y)
            i1, _ = gcd(h1, y)
            i0 += 1
            i1 += 1
            if i0 == iterations:
                new_candidates.add(h0)
            if i1 == iterations:
                new_candidates.add(h1)
        candidates = new_candidates

    if len(candidates) > 0:
        p.success("found %d candidates", len(candidates))
    else:
        p.failure("found no candidates")


for phi in candidates:
    phi += (1<<2047)
    log.info('phi=%s', f'{phi:b}')
    d = pow(e, -1, phi)
    key = RSA.construct((n, e, d))
    cipher = PKCS1_OAEP.new(key)
    log.info('d=%d', d)
    m = cipher.decrypt(flag)
    print(m.decode())
