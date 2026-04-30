#!/usr/bin/env python

from pwn import *

conn = remote('power-tower.ctf.wales', 40010)

conn.recvuntil(b'The super secret password is:\n\t')

password = conn.recvline()[:-1]
print('got password:', password)

password = list(password)
password[0], password[1], password[2], password[3] = password[2], password[3], password[0], password[1]
password = bytes(password)
print('permuted password:', password)

conn.recvuntil(b'> ')
conn.sendline(b'1')
conn.recvuntil(b'> ')
conn.sendline(password)
conn.recvuntil(b'Here is the output: ')
password_enc = conn.recvline()[:-1]

print('"encrypted" password:', password_enc)

conn.recvuntil(b'> ')
conn.sendline(b'2')
conn.recvuntil(b'> ')
conn.sendline(password_enc)
conn.recvuntil(b'Here is the flag: ')
flag = conn.recvline()[:-1]

conn.close()
print('flag:', flag)

