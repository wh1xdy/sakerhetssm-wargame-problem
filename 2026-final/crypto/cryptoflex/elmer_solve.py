from math import sqrt
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.number import *
from pwn import *

io = remote("localhost", 50000)

io.recvuntil(b"N: ")
N = int(io.recvline().strip())
io.recvuntil(b"e: ")
e = int(io.recvline().strip())

io.recvuntil(b"Choice: ")
io.sendline(b"1")
io.recvuntil(b"exponent: ")
io.sendline(b"0")

def set_exponent(n):
    io.recvuntil(b"Choice: ")
    io.sendline(b"1")
    io.recvuntil(b"exponent: ")
    io.sendline(str(n).encode())
    io.recvuntil(b"in ")
    iterations = int(io.recvuntil(b" ").strip())
    return iterations

def get_flag():
    io.recvuntil(b"Choice: ")
    io.sendline(b"3")
    io.recvuntil(b": ")
    flag = long_to_bytes(int(io.recvline(), 16))
    return flag

def decrypt(key: RSA, message: bytes) -> bytes:
    cipher = PKCS1_OAEP.new(key)
    return cipher.decrypt(message)

def gcd(a: int, b: int) -> tuple[int, int]:
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


BITS = 2048

b = "00"  

def dfs(b, depth):
    if depth == BITS - 1:
        print("1" + b,"\n")
        return int("1" + b, 2)

    b0 = "0" + b
    b1 = "1" + b

    p = 2 ** (depth + 1)
    iterations = set_exponent(p)

    iters0 = gcd(int(b0, 2), p)[0] + 1
    iters1 = gcd(int(b1, 2), p)[0] + 1

    if iters0 == iterations:
        return dfs(b0, depth + 1)
    if iters1 == iterations:
        return dfs(b1, depth + 1)

sys.setrecursionlimit(9999999)

print("Recovering phi...")
phi_guess = dfs(b, 2)
print(phi_guess)

assert phi_guess != None

a = N + 1 - phi_guess
from gmpy2.gmpy2 import isqrt

b = isqrt((a ** 2) // 4 - N)

p = int(abs(-a // 2 + b))
q = int(abs(-a // 2 - b))

print()
print(f"{p = }")
print()
print(f"{q = }")

flag_e = get_flag()

d = pow(e, -1, phi_guess)
key = RSA.construct((N, e, d, p, q), consistency_check=False)

flag = decrypt(key, flag_e)

print(flag)
