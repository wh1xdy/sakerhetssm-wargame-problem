import os
import math
def random_below(n):
    byte_count = math.ceil(n.bit_length() / 8)
    random_bytes = os.urandom(byte_count)
    random_number = int.from_bytes(random_bytes, byteorder="big") % n
    
    return random_number

above = 0
below = 0
runs = 1000000
for _ in range(runs):
    if random_below(192) > 95:
        above += 1
    else:
        below += 1
print(f"runs: {runs}")
print(f"above half: {above}")
print(f"below half: {below}")