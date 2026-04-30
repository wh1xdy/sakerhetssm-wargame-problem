import re
import numpy as np
from sage.all import *
import socket

def vec_from_str(s, size=None):
    l = list(int(x) for x in s.split(' '))
    if size:
        return l + [0] * (size - len(l))
    else:
        return l
    
    
def read_openfhe_vector(line, size=None):
    pat = re.compile(r'.* COEF: \[((\d+ ?)+)\]')
    m = pat.match(line)
    if m:
        v = vec_from_str(m[1], size)
        return v
    else:
        print('WARNING: no match for vector')
        return None
    
    
def to_centered_representaion(v, q):
    res = list(int(x) for x in v)
    for i in range(len(v)):
        if res[i] > q//2:
            res[i] -= q
    return res
    

# this is the actual sigma of the noise used in encryption
def compute_real_sigma_1(n):
    return 3.19 * sqrt(4/3 * n)
    
    
# this is the estimation by EXEC_NOISE_ESTIMATION mode of the noise used in fresh encryption
# is there a bug in OpenFHE implementation?
def compute_estimated_sigma_1(n):
    return 3.19 * sqrt(2/3 * n)
    

# estimated by EXEC_NOISE_ESTIMATION mode noise after computing t additions of fresh ciphertexts
def compute_estimated_sigma_2(n, t, statistical_param):
    return compute_estimated_sigma_1(n) * sqrt(12 * t) * 2**(statistical_param/2)


def compute_noise_factor(n, t, statistical_param):
    sigma_a = t * compute_real_sigma_1(n)
    sigma_b = compute_estimated_sigma_2(n, t, statistical_param)
    sigma = sqrt(sigma_a**2 + sigma_b**2)
    f = sigma_a**2 / sigma**2
    # f is the mu of t * e, we want mu of e, therefore, divide by t
    return float(f / t)
    
def read_parameters_from_file():
    filename = 'poly.txt'
    with open(filename, 'rt') as f:
        dim = f.readline()
        q = int(f.readline().split(' ')[-1])
        t = int(f.readline().split(' ')[-1])
        statistical_parameter = int(f.readline().split(' ')[-1])

        b = read_openfhe_vector(f.readline())
        n = len(b)

        a = read_openfhe_vector(f.readline(), size=n)

        etotal = read_openfhe_vector(f.readline(), size=n)
        etotal = to_centered_representaion(etotal, q)

    return t, statistical_parameter, n, q, b, a, etotal

# find x such that x = r_i mod a_i, x is not modulo prod a_i
def my_crt(r_list, a_list):
    M = 1
    for ai in a_list:
        M *= ai
    res = 0
    for ri, ai in zip(r_list, a_list):
        Mi = M // ai
        Mi_inv = inverse_mod(Mi, ai)
        res += ri * Mi * Mi_inv
    return res

def inverse_poly_mod_nonprime(a, n, q):
    assert(type(a) is list)
    qfactors = factor(q)
    qfactors = list(prime**power for prime, power in qfactors)
    ainv_polys = []
    for p in qfactors:
        Rix = PolynomialRing(IntegerModRing(p), 'x')
        gcd, ainv, _ = xgcd(Rix(a), Rix.gen()**n+1)
        assert(gcd == 1)
        ainv_polys.append(ainv.change_ring(Rx))
    ainv = my_crt(ainv_polys, qfactors)
    # hack
    return R(list(ainv))

t, statistical_parameter, n, q, b, a, etotal = read_parameters_from_file()

stat = statistical_parameter
n = len(b)
Rx = PolynomialRing(IntegerModRing(q), 'x')
xbar = Rx.gen()
R = Rx.quotient(xbar**n + 1, 'x')

scaled_etotal = list(int(round(etotal_i * compute_noise_factor(n, t, stat))) for etotal_i in etotal)
bprime = R(b) - R(scaled_etotal)

ainv = inverse_poly_mod_nonprime(a, n, q)
sprime = bprime * ainv * (-1)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('gone-but-not-forgotten.ctf.wales', 34567))
# read instructions
_ = s.recv(1024)
for c in sprime:
    s.send((str(c)+"\n").encode())
s.send("\n".encode())

res = s.recv(1024).decode()
s.close()
s = res.index("SCSC{")
e = res.index("}")
print(res[s:e+1])

