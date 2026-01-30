from pwn import *

conn = remote("localhost", 50000)
conn.recvline()

enc = conn.recvline().decode()#.split(". ")
#enc[-1] = enc[-1][:-2]

conn.recv(len(b"Test input to encode: "))
letters = list(map(chr, range(32, 127)))
conn.sendline("".join(letters).encode())

lettermap = conn.recvline().decode().split(". ")
lettermap[-1] = lettermap[-1][:-2]

dec = enc
for from_, to_ in zip(lettermap, letters):
    dec = dec.replace(from_, to_)

print(dec.replace(". ", ""))