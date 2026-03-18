from sage.all import *
from Crypto.Util.number import *

p = 13066000201421942542687362413814838251785406752799433725429188944459810152059583873406652805052769219175215757020978780767243160851942734086025885445160419
g = 2
bob_pk = 769264773511746431831938473119943550157449445919053274282288581623007989357066535664828302353044808323289463793888476961237564130789900545306611704557788
alice_pk = 11187272766463150546227651255966800907948780079206702921896593070419462724370411840463312722155587119905899884484141565637775866026966869008945337518548536

def BSGS(g, A, n, G):
    # Normally ceil(sqrt(n)) should work but for some reason some test cases break this
    m = ceil(sqrt(n)) + 1
    y = A
    log_table = {}

    for j in range(m):
        log_table[j] = (j, g**j)

    inv = g**-m
    
    for i in range(m):
        for x in log_table.keys():
            if log_table[x][1] == y:
                return i * m + log_table[x][0]
    
        y *= inv

    return None

# The Pohlig-Hellman attack on Diffie-Hellman works as such:
# Given the generator, public keys of either Alice or Bob, as well as the multiplicative order
# Of the group (which in Diffie-Hellman is p - 1 due to prime modulus), 
# one can factor the group order (which by construction here is B-smooth) into 
# Small primes.  By Lagrange's theorem, we have that


def pohlig_hellman(g, A, F, debug=True):
    """ Attempts to use Pohlig-Hellman to compute discrete logarithm of A = g^a mod p"""
    
    # This code is pretty clunky, naive, and unoptimized at the moment, but it works.

    p = F.order() 
    factors = [p_i ** e_i for (p_i, e_i) in factor(F.order() - 1)]
    crt_array = []

    if debug:
        print("[x] Factored |F_p| = p - 1 into %s" % factors)

    for p_i in factors:
        print("Print finding exponent mod", p_i)
        g_i = g ** ((p - 1) // p_i)
        h_i = A ** ((p - 1) // p_i)
        #x_i = BSGS(g_i, h_i, p_i, GF(p_i))
        x_i = discrete_log(h_i, g_i, p_i)
        if debug and x_i != None:
            print("[x] Found discrete logarithm %d for factor %d" % (x_i, p_i))
            crt_array += [x_i]
        elif x_i == None:
            print("[] Did not find discrete logarithm for factor %d" % p_i)


    return crt(crt_array, factors)

F = GF(p)
secret = pohlig_hellman(F(g), F(alice_pk), F)
print("Finding secret...")
print(secret)
print(long_to_bytes(secret))
