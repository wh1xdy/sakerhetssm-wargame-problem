#!/usr/bin/env python3

import itertools
import numpy as np

flag = b'DDC{travel_through_c3llul4r_aut0mata_space_time!!}'
width = 20
length = 50
bsize = 2
iters = 5

assert length == len(flag)

bits = bin(int.from_bytes(flag, 'big'))[2:].zfill(len(flag)*8)
assert len(bits) == width * width

grid = np.array([list(map(int, bits[i*width:i*width+width])) for i in range(width)])

assert grid.shape[0] % bsize == 0
assert grid.shape[1] % bsize == 0

for ts in range(iters):
    for bi, bj in itertools.product(range(width//bsize), range(width//bsize)):
        if ts % 2 == 0:
            bsi = bi*bsize
            bsj = bj*bsize
        else:
            bsi = bi*bsize-1
            bsj = bj*bsize-1

        grid[bsi,bsj], grid[bsi,bsj+1], grid[bsi+1,bsj], grid[bsi+1,bsj+1] = (
                grid[bsi,bsj], grid[bsi+1,bsj], grid[bsi,bsj+1], grid[bsi+1,bsj+1])
    #print(grid.flatten().dot(1 << np.arange(grid.size)[::-1]))

bits = ''.join(map(str, grid.flatten().tolist()))
scrambled_flag = []
for i in range(len(bits)//8):
    scrambled_flag.append(int(bits[i*8:i*8+8], 2))
print(scrambled_flag)

print(''.join(f'\\x{c:02x}' for c in scrambled_flag))
print(''.join(f'{c:02x}' for c in scrambled_flag))
print(grid)
