#!/usr/bin/env python3
# Solve script for 'Bullrun'.
# Copyright (C) 2025-present  David Bergström

from Cryptodome.PublicKey import ECC
from Cryptodome.Util.number import long_to_bytes
from pwn import *

conn = remote ('127.0.0.1', 50000, ssl=True)
# conn = process ('container/service')

conn.recvuntil (b'Serial number: ')
P_x = int (conn.recvline ().decode ('utf-8'))
conn.recvuntil (b'Model number: ')
Q_x = int (conn.recvline ().decode ('utf-8'))

P = ECC.EccXPoint (P_x, 'Curve25519')
Q = ECC.EccXPoint (Q_x, 'Curve25519')

conn.sendlineafter (b'> ', b'1')
conn.sendlineafter (b': ', b'0')
conn.recvuntil (b'secret: ')
g0 = int (conn.recvline ().decode ('utf-8'))
conn.sendlineafter (b'> ', b'1')
conn.sendlineafter (b': ', b'0')
conn.recvuntil (b'secret: ')
g1 = int (conn.recvline ().decode ('utf-8'))
conn.sendlineafter (b'> ', b'2')
conn.recvuntil (b'secrets: ')
encrypted_state_secrets = int (conn.recvline ().decode ('utf-8'))
conn.sendlineafter (b'> ', b'3')
conn.close ()

print ('Recovering e... ', end='', flush=True)
for e in range (1, 2 ** 16):
	if (Q * e).x == P.x:
		break
else:
	assert (False)

print ('done!')

print ('Brute-forcing state... ', end='', flush=True)
for i in range (2 ** 16):
	try:
		guess = (g0 << 16) + i
		point = ECC.EccXPoint (guess, 'Curve25519')
	except ValueError:
		continue
	s = (point * e).x
	r = (P * s).x
	if int((Q * r).x >> 16) != g1:
		continue
	break
else:
	assert (False)

s = (point * e).x
def f():
	global s
	r = (P * s).x
	s = (P * r).x
	return int((Q * r).x >> 16)

print ('done!')

assert (g1 == f())
state_secrets = encrypted_state_secrets ^ f()
print (long_to_bytes (state_secrets).decode ('utf-8'))

