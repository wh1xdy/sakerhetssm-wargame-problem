with open("output") as f:
    encrypted = bytearray(bytes.fromhex(f.read()))

from ctypes import CDLL

libc = CDLL("libc.so.6")

for j in range(3600 * 24 * 60):
    if j & 0xFFFF == 0: print(j)
    libc.srand(1737402307 - j)
    encrypted2 = encrypted[:]
    for i in range(len(encrypted)):
        rand = libc.rand() & 0xFF
        encrypted2[i] ^= (rand)
        #print(rand)

    if b"SSM{" in bytes(encrypted2):
        print(bytes(encrypted2))
        break