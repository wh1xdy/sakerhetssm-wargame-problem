from web3 import Web3
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

w3 = web3.Web3(web3.HTTPProvider(rpc))

with open("FakeSetup.json", "r") as openfile:
    setup_abi = json.load(openfile)

"""
with open("abi/Store.json", "r") as openfile:
    store_abi = json.load(openfile)



setup_contract = w3.eth.contract(address=target_addr, abi=setup_abi)
"""

my_addr = w3.eth.account.from_key(private_key).address

"""
store_addr = setup_contract.functions.store().call()
print(f"{store_addr = }")

contract = w3.eth.contract(address=store_addr, abi=store_abi)
"""
print("My balance:", w3.eth.get_balance(my_addr) / 10**18)

#setup_contract.functions.hello().transact({"from": my_addr, "gas": 100000})

#solved = setup_contract.functions.isSolved().call()

#
# SKRIV DIN KOD HÄR!!!
#

setup_contract = w3.eth.contract(address=target_addr, abi=setup_abi)
setup_contract.functions.hello().transact({"from": my_addr, "gas": 100000})

secret_address = setup_contract.functions.secret().call()

print(f"{secret_address = }")

bytecode = w3.eth.get_code(secret_address)


# Define the slot numbers based on the decompiled code
slots = {
    '_solved': 0,
    '_wow': 1,
    'stor_2': 2,
    'stor_3': 3,
    'stor_4': 4
}

# Define the variable types
var_types = {
    '_solved': 'bool',
    '_wow': 'uint256',
    'stor_2': 'uint256',
    'stor_3': 'uint256',
    'stor_4': 'uint256'
}

# Function to retrieve and convert storage values
def get_storage_variable(address, slot, var_type='uint256'):
    value_bytes = w3.eth.get_storage_at(address, slot)
    if var_type == 'bool':
        # Boolean is 0x00 or 0x01 in the first byte
        value = bool(int.from_bytes(value_bytes[:1], byteorder='big'))
    elif var_type == 'uint256':
        value = int.from_bytes(value_bytes, byteorder='big')
    else:
        # Handle other types if necessary
        value = value_bytes.hex()
    return value

def dump():
    for var_name, slot in slots.items():
        var_type = var_types[var_name]
        value = get_storage_variable(secret_address, slot, var_type)
        print(f"{var_name}: {value}")


def generate_selector(signature):
    return w3.keccak(text=signature).hex()[:10]

# Function to call 'wow()' without ABI
def call_wow():
    data = "c75b5069"
    tx = {
        'to': secret_address,
        'data': data,
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(my_addr),
        'chainId': w3.eth.chain_id,
    }
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"'wow' transaction receipt: {receipt}")

# Function to call custom function with selector '0xdc5c64c0'
def call_custom_function():
    selector_custom = "dc5c64c0"
    data_custom = selector_custom
    tx = {
        'to': secret_address,
        'data': data_custom,
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(my_addr),
        'chainId': w3.eth.chain_id,
    }
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Custom function transaction receipt: {receipt}")

def call(f):
    function_selector = Web3.keccak(text=f)[:4]
    result = w3.eth.call({
        'to': secret_address,
        'data': function_selector
    })
    return result

def call_addr(fs):
    result = w3.eth.call({
        'to': secret_address,
        'data': fs
    })
    return result

# write bytecode as hex
with open("bytecode.hex", "w") as f:
    f.write(bytecode.hex())

# Ensure block number conditions
while w3.eth.block_number <= 40:
    print(f"{w3.eth.block_number = }")
    setup_contract.functions.hello().transact({"from": my_addr, "gas": 100000})

dump()
print(f"{w3.eth.block_number = }")

for i in range(11):
    call_wow()

call_custom_function()

for i in range(40-11):
    call_wow()

for i in range(23):
    call_custom_function()

for i in range(1):
    call_wow()


function_selector = '0xb8b8d35a'  # Function selector for solve(uint256)
amount = 123123
encoded_amount = hex(amount)[2:].zfill(64)  # 32-byte zero-padded hex
calldata = function_selector + encoded_amount

nonce = w3.eth.get_transaction_count(my_addr)
tx = {
    'to': secret_address,
    'data': calldata,
    'gas': 200000,
    'gasPrice': w3.eth.gas_price,
    'value': 0,  # Adjust if ETH is required
    'nonce': nonce,
    'chainId': w3.eth.chain_id,
}
signed_tx = w3.eth.account.sign_transaction(tx, private_key)

# Send the transaction
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f"Transaction completed: {receipt.transactionHash.hex()}")

print(f"{w3.eth.block_number = }")
dump()


#contract.functions.buyItem(1).transact({"value": 50 * 10**18, "from": my_addr})

solved = setup_contract.functions.isSolved().call()



print(f"{solved = }")


if solved:
    io.close()
    io = remote(IP, PORT)
    io.sendlineafter(b"> ", b"3")
    io.sendlineafter(b": ", uuid.encode())
    print(io.recvuntil(b"done :)").decode()) # print flag
