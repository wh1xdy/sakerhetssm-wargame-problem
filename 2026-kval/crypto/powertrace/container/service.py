#!/usr/bin/python3
from secret import flag, a, b, p, order, G
from secrets import randbelow

I = "Identity"

def correctness(x0, x):
    rev = lambda x: int(bin(x)[2:][::-1].ljust(order.bit_length(), "0"), 2)
    msb = 1 - abs(x0 - x).bit_length() / order.bit_length()
    lsb = 1 - abs(rev(x0) - rev(x)).bit_length() / order.bit_length()

    return msb, lsb

def add(P, Q):
    if P == I:
        return Q
    if Q == I:
        return P
    if P[0] == Q[0] and P[1] == -Q[1] % p:
        return I
    
    if P == Q:
        c = ((3*P[0]**2 + a) * pow(2*P[1], -1, p)) % p
    if P != Q:
        c =  ((Q[1] - P[1]) * pow(Q[0] - P[0], -1, p)) % p
    
    x = (c**2 - P[0] - Q[0]) % p
    y = (c*(P[0] - x) - P[1]) % p
    
    return (x, y)

def double_and_add(P, n):
    Q = P
    R = I
    power_cost = 0

    while n > 0:
        if n & 1:
            R = add(R, Q)
            power_cost += 1

        Q = add(Q, Q)
        power_cost += 1

        n >>= 1
    return power_cost, R

assert double_and_add(G, order)[1] == I

x = randbelow(order)

assert order.bit_length() == 380
attempts = 200

for i in range(attempts):
    inp = int(input())
    assert inp >= 0

    cost, _ = double_and_add(G, (x + i*inp) % order)
    print(cost)

x0 = int(input())
msb, lsb = correctness(x0, x)

print(f"You were {int(100*msb)}% accurate! (consecutive most significant bits)")
print(f"You were {int(100*lsb)}% accurate! (consecutive least significant bits)")

if x == x0:
    print("A freshly leaked flag, just for you!")
    print(flag)
else:
    print("too bad")
