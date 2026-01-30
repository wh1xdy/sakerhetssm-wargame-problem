import randcrack
from random import getrandbits
from pwn import *
from time import time

start = time()

#conn = remote("LOCALHOST", "1337", ssl=True)
conn = process("./container/service")

_ = conn.recvline()
_ = conn.recvline()
_ = conn.recvline()
_ = conn.recv(len('  Start slot machine'))
conn.sendline(b"")
print("passed start")

def decode_dice(rolls: list) -> int:
    assert len(rolls) == 32
    val = 0
    for idx, roll in enumerate(rolls):
        x = (roll - 1) % 2
        val += (x << idx)
    
    return val

rnd_bits = 0
rnd_data = 0
def roll_a_dice (rand):
    global rnd_bits
    global rnd_data
    if rnd_bits < 32:
        rnd_data |= rand.predict_getrandbits(32) << rnd_bits
        rnd_bits += 32
    x = rnd_data & ((1 << 32) - 1)
    rnd_data >>= 1
    rnd_bits -= 1
    return (x % 6) + 1

def increment_rand(rand, bits):
    global rnd_bits
    global rnd_data

    while bits:
        if rnd_bits < 32:
            rnd_data |= rand.predict_getrandbits(32) << rnd_bits
            rnd_bits += 32

        rnd_data >>= 1
        rnd_bits -= 1
        bits -= 1

def winnings(stakes, score):
	if score >= 25:
		return int (score * 0.25) * stakes
	elif score >= 16:
		return 2 * stakes
	else:
		return int (score * stakes / 16)

def get_random(vals: list):
    r = randcrack.RandCrack()
    for val in vals:
        r.submit(val)
    return r

def gimmie_coin(conn, coin: int):
    rolls = []
    conn.recvlines(3)

    tmp = conn.recv(len("Select action... "))
    #print(f"\"Select action... \" = {tmp}")
    conn.sendline(b"1")
    tmp = conn.recv(len("Insert coins: "))
    #print(f"\"Insert coins: \" = {tmp}")
    conn.sendline(str(coin).encode())

    cdice = 3
    while cdice:
        ndice = 0
        tmp = conn.recvline()
        tmp = conn.recvline()
        coins = int(tmp.split(b" ")[2].decode())
        #tmp = conn.recvline()
        #print(tmp)
        tmp = conn.recv(len(b"Roll...? "))
        conn.sendline(b"")
        #print(f"Roll...? = {tmp}")

        #tmp = conn.recvline()
        #conn.sendline(b"")
        
        for _ in range(cdice):
            recv = conn.recvline()
            num = int(recv[9].to_bytes(1).decode())
            #print(f"{num = }")
            if num == 6:
                ndice += 2

            rolls.append(num)
        cdice = ndice

        exta = conn.recvline()
        #print(f"{exta = }")
        tmp = conn.recv(len('Continue?'))
        conn.sendline(b"")
    
    conn.recvuntil(b", earning you ")
    add_coins = int(conn.recvuntil(b" KebabCoin! ", drop=True).decode())
    conn.sendline(b"")
    #print(f"{add_coins = }")

    return rolls, add_coins

def do_gamble(rand):
    x = 1

    score = 0
    cdice = 3
    while cdice > 0:
        ndice = 0
        for _ in range (cdice):
            value = roll_a_dice (rand)
            if value == 6:
                ndice += 2
            else:
                score += value
        cdice = ndice
    w = winnings (x, score)

    return w

coins = 10_000

roll_rolls = []
while len(roll_rolls) < 19968:
    coins -= 1
    rolls, add_coins = gimmie_coin(conn, 1)
    coins += add_coins
    roll_rolls.extend(rolls)
    print(f"\r{len(roll_rolls)} out of 19968 bits obtained", end="")
print()

offset = len(roll_rolls) - 19968

print(f"{len(roll_rolls) = }")
print(f"{coins = }")

vals = []
for idx in range(0, 19968, 32):
    vals.append(decode_dice(roll_rolls[idx : idx+32]))

assert len(vals) == 624

rand = get_random(vals)
increment_rand(rand, offset)

#coins = int(conn.recvline().split(b" ")[1].decode())
#context.log_level = "debug"

while coins < 13379876543210:
    potential = do_gamble(rand)
    #print(f"{potential = }")
    print(f"\r{coins = } out of 13379876543210", end="")

    if potential > 1:
        _, add_coins = gimmie_coin(conn, coins >> 1)
        coins -= coins >> 1
    else:
        coins -= 1
        _, add_coins = gimmie_coin(conn, 1)

    coins += add_coins
print()

conn.sendline(b"2")
conn.sendline(b"3")

flag = conn.recvlines(12)
print(b"\n".join(flag).decode())
conn.close()

print(f"solve took {time() - start} seconds")