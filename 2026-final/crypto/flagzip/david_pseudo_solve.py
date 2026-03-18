#!/usr/bin/env python
#
# Detta kan vara ett av de mest wacky "solve scripts" som jag någonsin
# har skrivit (om det ens kan kallas för ett "solve script"...).
# Kort förklarat, du startar solve scriptet och sedan interagerar du
# med det, och skriver in vad du tror är de första N tecken i flaggan.
# Skriptet kommer sedan att kasta ut ett förslag på bokstav N+1 samt
# en "poäng" som ska vara så låg som möjligt.  Ibland går det här fel,
# vilket är varför det behövs mänsklig interaktion med solve skriptet
# för att lösa uppgiften (jag var för lat för att programmatiskt
# detektera när det går fel).
#
# Exempel på interaktion:
# < SSM{
# > ['b'] 123
# < SSM{b
# > ['r'] 123
# < SSM{br
# > ['u'] 123
# < SSM{bru
# > ['h'] 123
# < SSM{bruh
# > ['}'] 123
# Användaren kan här dra slutsatsen att flaggan är SSM{bruh} (vilket
# den inte är).

from pwn import *

conn = process('container/service')

def query(msg):
    conn.recvuntil(b'encrypt: ')
    conn.sendline(msg.encode('utf-8'))
    conn.recvuntil(b'ciphertext: ')
    return len(conn.recvline())

ALPHA = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-,.;:!@#$%&/()=?[]{}*'

def getnext(known):
    candidates = []
    best = 100000000
    for c in ALPHA:
        n = sum([query(known + c) for _ in range(10)])
        if n > best:
            continue
        if n < best:
            best = n
            candidates = []
        candidates.append(c)
    return candidates, best

while True:
    inp = input()
    c, b = getnext(inp)
    while len(c) > 1:
        c, b = getnext(inp)
    print(c, b)
