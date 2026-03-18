from sage.all import *
import secrets
from Crypto.Util.number import *
from mpmath import mp, atan, mpf

from chall import ComplexInteger

Zi = ZZ[i] 

e = 65537
R = RealField(4096)

with open("output.txt", "r") as f:
    f.read(4)
    n = f.readline().strip()
    nl, nr = n.split(" ", 1)
    nR = int(nl)
    nI = (-1 if nr[0] == "-" else 1) * int(nr[2:-2])

    f.readline()
    f.read(4)
    c = f.readline().strip()
    cl, cr = c.split(" ", 1)
    cR = int(cl)
    cI = (-1 if cr[0] == "-" else 1) * int(cr[2:-2])

    f.read(49)
    p_arg_s = f.readline().strip()
    p_arg = R(p_arg_s)

    print(f"{p_arg = }")
    print(f"{nR = }")
    print(f"{nI = }")
    print(f"{cR = }")
    print(f"{cI = }")

frac = continued_fraction(tan(p_arg)).convergents()[-2]
b, a = frac.numerator(), frac.denominator()

n_norm = nR ** 2 + nI ** 2
p = a ** 2 + b ** 2
q = int(n_norm // p)

print(n_norm)
print(p)
print(q)

assert n_norm % p == 0
assert is_prime(p)
assert is_prime(q)

phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)

def powmod(a, b, m):
    # Square and multiply algorithm
    result = ComplexInteger(1, 0)
    base = a % m

    while b > 0:
        if b % 2 == 1:
            result = (result * base) % m
        base = (base * base) % m
        b //= 2

    return result

m = powmod(ComplexInteger(cR, cI), d, ComplexInteger(nR, nI))
print(m)
print(long_to_bytes(m.a) + long_to_bytes(m.b))
