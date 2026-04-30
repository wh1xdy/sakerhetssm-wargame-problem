#!/usr/bin/env python3

import itertools
import numpy as np

scrambled_flag = [84, 17, 19, 219, 252, 54, 37, 62, 207, 76, 78, 48, 56, 216, 205, 37, 50, 48, 215, 235, 38, 56, 62, 253, 206, 33, 50, 31, 203, 223, 101, 48, 55, 201, 214, 96, 26, 57, 240, 227, 35, 53, 29, 116, 203, 105, 48, 51, 171, 253]

width = 20
iters = 5

bits = bin(int.from_bytes(bytes(scrambled_flag), 'big'))[2:].zfill(len(scrambled_flag)*8)
grid = np.array([list(map(int, bits[i*width:i*width+width])) for i in range(width)])

bsize = 2
assert grid.shape[0] % bsize == 0
assert grid.shape[1] % bsize == 0

for ts in range(iters-1, -1, -1):
    for bi, bj in itertools.product(range(width//bsize), range(width//bsize)):
        if ts % 2 == 0:
            bsi = bi*bsize
            bsj = bj*bsize
        else:
            bsi = bi*bsize-1
            bsj = bj*bsize-1

        grid[bsi,bsj], grid[bsi,bsj+1], grid[bsi+1,bsj], grid[bsi+1,bsj+1] = (
                grid[bsi,bsj], grid[bsi+1,bsj], grid[bsi,bsj+1], grid[bsi+1,bsj+1])

bits = ''.join(map(str, grid.flatten().tolist()))
flag = []
for i in range(len(bits)//8):
    flag.append(int(bits[i*8:i*8+8], 2))
print(bytes(flag))
