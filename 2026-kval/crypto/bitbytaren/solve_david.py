#!/usr/bin/env python

with open('output.txt', 'r') as f:
    lines = f.readlines()

ans = []
for i in range(len(lines[0])):
    num_zero = 0
    num_one = 0
    for l in lines:
        if l[i] == '0':
            num_zero += 1
        elif l[i] == '1':
            num_one += 1
    if num_zero == 0 and num_one == 0:
        break
    if num_zero > num_one:
        ans.append('0')
    else:
        ans.append('1')

print(''.join(ans)) # toss it into CyberChef
