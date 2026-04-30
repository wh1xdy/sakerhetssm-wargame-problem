#!/usr/bin/env python3

print()
for x in range(10):
    for y in range(10):
        print(f'SET_BIT_AT(BIT_AT({(x*2-1)%20}, {(y*2+1-1)%20}), {(x*2+1-1)%20}, {(y*2-1)%20});')
        print(f'SET_BIT_AT(BIT_AT({(x*2+1-1)%20}, {(y*2-1)%20}), {(x*2-1)%20}, {(y*2+1-1)%20});')

for x in range(10):
    for y in range(10):
        print(f'SET_BIT_AT(BIT_AT({x*2}, {y*2+1}), {x*2+1}, {y*2});')
        print(f'SET_BIT_AT(BIT_AT({x*2+1}, {y*2}), {x*2}, {y*2+1});')

