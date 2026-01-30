import random
from tqdm import tqdm
from Crypto.Util.number import *

for i in tqdm(range(100000000)):
    p = random.randint(10**0x14A, 10**0x14C)
    q = random.randint(10**0x14A, 10**0x14C)

    n = long_to_bytes(p * q)

    if n[0x110:].startswith(b"sh\x00"):
        print("Found p and q!")
        print(p, q)
        break
