from pwn import *
from Crypto.Util import number

HOST, PORT = 'localhost', 50000

def str_to_int(x):
    return number.bytes_to_long(x.encode())

def LCG(x):
    return (a*x + b) % n

def LCG_rev(x):
    return ((x-b) * pow(a, -1, n)) % n

io = remote(HOST, PORT)

a = int(io.recvregex(rb'a = (\d+)\n', capture=True).group(1))
b = int(io.recvregex(rb'b = (\d+)\n', capture=True).group(1))
n = int(io.recvregex(rb'n = (\d+)\n', capture=True).group(1))


x = LCG_rev(LCG_rev(LCG_rev(str_to_int("A whole new world..."))))
io.sendline(str(x).encode())
print(io.recvall().decode())