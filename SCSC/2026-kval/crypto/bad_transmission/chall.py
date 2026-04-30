from sage.all import *
p = 2**255 - 19
PR = GF(p)['x']

secret = PR.random_element(degree=200).monic()
secret += ZZ.from_bytes(os.environ.get('FLAG', 'flag{here}').encode()) - secret(0)

errbits = 8
with open('output.txt', 'w') as o:
    for i in range(3):
        f = PR.random_element(degree=20).monic() * secret
        f += PR([randint(-2**errbits, 2**errbits) for _ in range(f.degree())])
        o.write(f'{f}\n')