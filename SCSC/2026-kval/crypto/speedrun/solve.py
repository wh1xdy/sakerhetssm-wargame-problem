from sage.all import *
from pwn import *
from time import time

context.log_level = "debug"

p = 1153314233165211801192267409330155318946479505056513196790508370956838929031628141

F = GF(p)
E_ = EllipticCurve(F, [0, 1])
assert E_.is_supersingular()

jinv = lambda a, b: 1728*4*a**3 / (4*a**3+27*b**2)
j_inv = jinv(E_.a4(), E_.a6())

def next_curve(E):
    # print("computing isogeny... ", end="")
    sys.stdout.flush()

    p = E.base_field().characteristic()

    R = E.random_point()
    while (((p+1)//3) * R).is_zero():
        R = E.random_point()

    ret = E.isogeny_codomain(((p+1)//3) * R)
    # print("done.")
    # print(f"curves: {E} to {ret}")
    return ret

def give_b(j_inv, a):
    # j_inv = 1728*4a^3 / (4a^3 + 27b^2)
    # 4a^3 + 27b^2 = 1728*4a^3 / j_inv
    # b^2 = (1728*4a^3 / j_inv - 4a^3) / 27

    j_inv = F(j_inv)
    a = F(a)

    _27b2 = 1728*4*a**3 * j_inv.inverse() - 4*a**3
    b2 = _27b2 * F(27).inverse()

    if not b2.is_square():
        return None

    b = b2.sqrt()
    assert jinv(a, b) == j_inv

    return b

def loop_till_b(E, a, j_inv):
    if j_inv != 0:
        b = give_b(j_inv, a)
    else: 
        b = None
    while b is None or j_inv == 0:
        # print(f"{j_inv = }")
        E = next_curve(E)
        j_inv = jinv(E.a4(), E.a6())
        if j_inv != 0:
            b = give_b(j_inv, a)
        else: 
            b = None

    return (b, (E, j_inv))


start = time()
# conn = process(["python3", "./container/chall.py"])
conn = remote("0.0.0.0", 50000)

rounds = 500
for i in range(rounds):
    print(f"doing pass {i+1} of {rounds}")
    a = int(conn.recvline().decode())
    _ = int(conn.recvline().decode())

    b, (E_, j_inv) = loop_till_b(E_, a, j_inv)
    E = EllipticCurve(F, [a, b])
    assert E.is_supersingular()
    G = E.gens()[0]
    (Gx, Gy) = G.xy()

    conn.sendline(str(Gx).encode())
    conn.sendline(str(Gy).encode())

    P = eval(conn.recvline().decode())
    P = E(P)
    # print(f"{E = }")
    # print(f"{E.order().factor() = }")

    x = P.log(G)
    conn.sendline(str(x).encode())

end = time()
print(f"solve took {end-start} seconds")
conn.interactive()
