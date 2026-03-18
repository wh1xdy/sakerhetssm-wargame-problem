#!/usr/bin/env python3

import Crypto.PublicKey.ECC as ECC
from Crypto.Util.number import long_to_bytes
from Crypto.PublicKey._point import EccXPoint

from tqdm import tqdm

from pwn import remote, process

params = ECC.generate(curve='Curve25519')
conn = process("./container/service")
conn.recvline()

# leak P
Px = int(conn.recvline().decode().split(": ")[1])
Qx = int(conn.recvline().decode().split(": ")[1])
P = EccXPoint(Px, "Curve25519")
Q = EccXPoint(Qx, "Curve25519")
assert Qx == Q.x, f"Qx {Qx} Q.x {Q.x}"

print("bruting P Q secret")
for i in tqdm(range(1, 2**16)):
    if Q*i == P:
        m = i
        break
else:
    exit("uh oh")

print(f"16-bit {i}")

conn.recvlines(4)
conn.sendline(b"1")
# conn.recvline()
conn.sendline(b"0")
sec = int(conn.recvline().decode().split(": ")[2])


def f():
    global s
    r = (P * s).x
    s = (P * r).x
    return int((Q * r).x >> 16)


conn.recvlines(4)
conn.sendline(b"2")
enc = int(conn.recvline().decode().split(": ")[1])

print("bruting flag")
for add in tqdm(range(2**16)):
    Q2 = EccXPoint((sec << 16) + add, "Curve25519")
    P2 = Q2 * m
    s = P2.x

    out = f()
    mflag = out ^ enc
    try:
        byt = long_to_bytes(mflag).decode()
    except:
        continue

    if "SSM{" in byt:
        flag = byt
        break

print(flag)
