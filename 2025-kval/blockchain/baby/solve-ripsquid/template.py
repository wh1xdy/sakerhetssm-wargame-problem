import web3
import json
from pwn import *
import subprocess

IP = "localhost"
PORT = 50000

io = remote(IP, PORT)

io.sendlineafter(b"> ", b"1")

pow_yay = io.recvline()[:-1].decode()
pow_res = subprocess.check_output(pow_yay, shell=True).decode().strip()
io.sendlineafter(b"Solution please: ", pow_res.encode())

io.recvuntil(b"Blockchain info:\n")

uuid = io.recvline().strip().decode().split(" ")[-1]
rpc = io.recvline().strip().decode().split(" ")[-1]
rpc = rpc.replace("[ip]", IP)
private_key = io.recvline().strip().decode().split(" ")[-1]
my_addr = io.recvline().strip().decode().split(" ")[-1]
target_addr = io.recvline().strip().decode().split(" ")[-1]

print(f"{uuid = }")
print(f"{rpc = }")
print(f"{private_key = }")
print(f"{my_addr = }")
print(f"{target_addr = }")

with open("abi/Store.json", "r") as openfile:
    store_abi = json.load(openfile)

with open("abi/Setup.json", "r") as openfile:
    setup_abi = json.load(openfile)

w3 = web3.Web3(web3.HTTPProvider(rpc))
setup_contract = w3.eth.contract(address=target_addr, abi=setup_abi)
my_addr = w3.eth.account.from_key(private_key).address

store_addr = setup_contract.functions.store().call()
print(f"{store_addr = }")

contract = w3.eth.contract(address=store_addr, abi=store_abi)

print("My balance:", w3.eth.get_balance(my_addr) / 10**18)

setup_contract.functions.hello().transact({"from": my_addr, "gas": 100000})

solved = setup_contract.functions.isSolved().call()
print("Is solved?", solved)

#
# SKRIV DIN KOD HÄR!!!
#

contract.functions.buyItem(1).transact({"value": 50 * 10**18, "from": my_addr})

solved = setup_contract.functions.isSolved().call()
print("Is solved?", solved)

if solved:
    io.close()
    io = remote(IP, PORT)
    io.sendlineafter(b"> ", b"3")
    io.sendlineafter(b": ", uuid.encode())
    print(io.recvuntil(b"done :)").decode()) # print flag

#io.interactive()
