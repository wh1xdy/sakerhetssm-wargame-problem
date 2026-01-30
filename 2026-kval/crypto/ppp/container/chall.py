#!/usr/bin/python3
from Crypto.Util.number import bytes_to_long, getPrime
from secrets import randbelow
from flag import flag
flag = bytes_to_long(flag)

def banner():
   print(

"""
 ███████████  ███████████  ███████████ 
░░███░░░░░███░░███░░░░░███░░███░░░░░███
 ░███    ░███ ░███    ░███ ░███    ░███
 ░██████████  ░██████████  ░██████████ 
 ░███░░░░░░   ░███░░░░░░   ░███░░░░░░  
 ░███         ░███         ░███        
 █████        █████        █████       
░░░░░        ░░░░░        ░░░░░        
"""

) 

def menu():
    print("""The oracle presents.
[P]ad message
[C]hange padding
[R]SA padded flag
E[x]it""")

def encrypt(flag, padding):
    return pow(padding(flag), 137, n)

def new_pad():
    leng = 17 + randbelow(30 - 17)
    coefs = [randbelow(n) for _ in range(leng)]
    
    return lambda x: sum([coef * pow(x, i, n) for i, coef in enumerate(coefs)]) % n

n = getPrime(1024) * getPrime(1024)
padding = new_pad()

banner()
while True:
    menu()
    inp = input().lower()
    
    if inp == "p":
        x = int(input("x = ").strip())
        print(f"y = {padding(x)}")
    
    elif inp == "c":
        padding = new_pad()
    
    elif inp == "r":
        print(f"encrypted = {encrypt(flag, padding)}")
    
    elif inp == "x":
        print("jevil")
        exit(0)
