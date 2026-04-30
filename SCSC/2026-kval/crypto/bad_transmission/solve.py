from sage.all import *
import itertools
from re import findall
from subprocess import check_output

def cvp(B, t):
    t = vector(ZZ, t)
    B = flatter(B)
    S = B[-1].norm().round()+1
    L = block_matrix([
        [B,         0],
        [matrix(t), S]
    ])
    for v in flatter(L):
        if abs(v[-1]) == S:
            return t - v[:-1]*sign(v[-1])
    raise ValueError('cvp failed?!')

def flatter(M):
    z = "[[" + "]\n[".join(" ".join(map(str, row)) for row in M) + "]]"
    ret = check_output(["flatter"], input=z.encode())
    return matrix(M.nrows(), M.ncols(), map(int, findall(b"-?\\d+", ret)))

p = 2**255 - 19
Fp = GF(p)
PR = Fp['x']

with open('output.txt', 'r') as o:
    inp_polys = [PR(l) for l in o.readlines()]

def shift_matrix(f, npows):
    return matrix(npows, f.degree()+npows, lambda i, j: f[j-i])

to_vec = lambda poly: vector(Fp, poly.list())
to_poly = lambda vec: PR(list(vec))

# we first find linear combinations (over F[x]) which annihilate
# the noise-free polynomials via a classical orthogonal lattice setup
npows = 20
S = block_matrix([[shift_matrix(f, npows)] for f in inp_polys])
L = block_matrix(ZZ, [
    [S, 1],
    [p, 0]
])

print(f'reducing {L.dimensions()} lattice...')
L = flatter(L)

# recover the small polynomials secret was multiplied by
ortho_polys = [
    [to_poly(coeffs) for coeffs in itertools.batched(row[S.ncols():], npows)]
    for row in L[:len(inp_polys)]
]

mults = matrix(ortho_polys).right_kernel_matrix()[0]

# we now recover the noise-free polynomial by finding
# close vectors in the lattice of multiples of mults[i]
# to our noisy polynomials
r_deg = 200
for i, mult in enumerate(mults):
    S = shift_matrix(mult, r_deg+1)
    L = identity_matrix(S.ncols())*p
    L.set_block(0, 0, S.rref().change_ring(ZZ))

    print(f'cvp in {L.dimensions()} lattice...')
    r = to_poly(cvp(L, to_vec(inp_polys[i]).change_ring(ZZ))) // mult
    flag = ZZ(r[0]).to_bytes(32).strip(b'\0')
    print(flag.decode())
    break # they all print the same thing