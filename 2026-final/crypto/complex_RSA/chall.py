from math import gcd, lcm
import secrets
from secret import FLAG
from Crypto.Util.number import *
from mpmath import ceil, floor, mp, atan, mpc, mpf

mp.dps = 1000

class ComplexInteger:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __add__(self, other):
        return ComplexInteger(self.a + other.a, self.b + other.b)

    def __sub__(self, other):
        return ComplexInteger(self.a - other.a, self.b - other.b)

    def __mul__(self, other):
        return ComplexInteger(self.a * other.a - self.b * other.b, self.a * other.b + self.b * other.a)

    def __floordiv__(self, other):
        return self.__divmod__(other)[0]

    def __mod__(self, other):
        return self.__divmod__(other)[1]

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b

    def __str__(self):
        if self.a == self.b == 0:
            return "0"
        if self.a == 0:
            return f"{self.b}*i"
        if self.b == 0:
            return f"{self.a}"
        return f"{self.a} {'+' if self.b > 0 else '-'} {abs(self.b)}*i"

    def arg(self):
        return atan(mpf(self.b) / mpf(self.a))

    def conjugate(self):
        """
        Returns the complex conjugate of this complex integer
        """
        return ComplexInteger(self.a, -self.b)

    def __divmod__(self, other):
        def round_to_even(n):
            ipart = floor(n)
            fpart = n - ipart

            if fpart < 0.5:
                return int(ipart)
            elif fpart > 0.5:
                return int(ceil(n))
            else: # fpart == 0.5
                if ipart % 2 == 0:
                    return int(ipart)
                else:
                    return int(ipart + 1)

        z = mpc(self.a, self.b) / mpc(other.a, other.b)
        qx = round_to_even(z.real)
        qy = round_to_even(z.imag)

        q = ComplexInteger(qx, qy)
        r = self - other * q
        return q, r

    def norm(self):
        """
        Returns the complex norm
        """
        return self.a ** 2 + self.b ** 2

    def is_prime(self):
        """
        Returns whether or not this is a gaussian prime
        """
        if self.b == 0:
            if self.a > 0 and self.a % 4 == 3 and isPrime(self.a):
                 return True
        
        if self.a == 0:
            if self.b > 0 and self.b % 4 == 3 and isPrime(self.b):
                 return True
                 
        return isPrime(self.norm())

def get_gaussian_prime(nbit):
    while True:
        a = secrets.randbits(nbit)
        b = secrets.randbits(nbit)

        C = ComplexInteger(a, b)
        if C.is_prime():
            return C

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

p = get_gaussian_prime(512)
q = get_gaussian_prime(512)
n = p * q

e = 0x10001

fl = len(FLAG)
m = ComplexInteger(bytes_to_long(FLAG[:fl//2]), bytes_to_long(FLAG[fl//2:]))
c = powmod(m, e, n)

print(f"n = {n}")
print(f"e = {e}")
print(f"c = {c}")
print(f"Its so secure, ill even point you to where p is! {p.arg()}")
