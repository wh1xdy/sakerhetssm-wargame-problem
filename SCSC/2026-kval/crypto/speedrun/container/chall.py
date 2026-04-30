#!/usr/bin/env python3
import signal
from secrets import randbelow
from flag import flag

def timeout(signum, frame):
    print("Too slow!")
    exit(1)

I = "Identity"
def add(ab, P, Q):
    a, b = ab

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

def mul(ab, n, P):
    Q = P
    R = I
    while n:
        if n & 1:
            R = add(ab, R, Q)
        Q = add(ab, Q, Q)
        n >>= 1
    return R


p = 1153314233165211801192267409330155318946479505056513196790508370956838929031628141
TIMEOUT = 300
signal.signal(signal.SIGALRM, timeout)
signal.alarm(TIMEOUT)

for _ in range(500):
    a = randbelow(p)
    b = randbelow(p)
    print(a)
    print(b)
    x = randbelow(p)

    Gx = int(input())
    Gy = int(input())
    G = (Gx, Gy)
    print(mul((a, b), x, G))

    x_ = int(input())
    if x_ != x:
        print("Wrong answer!")
        exit(1)

print(flag)

