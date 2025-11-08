#!/usr/bin/env python3

from pwn import *
import secrets
import time
import subprocess

HOST = 'localhost'
PORT = 50000

io = remote(HOST, PORT, level='info')
#io = process(['python3', 'tmp/apparatus.py'], stderr=sys.stdout)
#io = process(['python3', 'tmp/apparatus.py'], stderr=subprocess.DEVNULL)

io.recvline_contains(b'Eventually, a magidiced flagfish falls out.')
flag_enc = bytes.fromhex(io.recvline().decode().strip())
log.info('Flag encrypted: %s', flag_enc.hex())


def attempt(data: bytes) -> float:
    t0 = time.time()
    io.sendline(data.hex().encode())
    io.recvline().decode().strip()
    t1 = time.time()
    dt = t1 - t0
    return dt


blocks = []
while len(flag_enc) > 16:
    block = []
    with log.progress(f'Decrypting block {len(blocks)+1}') as p:
        while len(block) < 16:
            #log.info('Current block: %s', block[::-1])
            p.status('Current block: %s', block[::-1])
            best_t = 0
            best_guess = None
            for guess in range(256):
                dts = []
                for sample in range(5):  # p(fail) = 0.2^5 ~= 0.0003
                    cand_block = bytes((block + [guess])[::-1]).rjust(
                        16, bytes([random.randint(0, 255)]))

                    padlen = len(block) + 1
                    padding = bytes([padlen] * padlen).rjust(16, b'\0')
                    cand_block = bytes(x ^ y ^ z for x, y, z in zip(
                        cand_block, padding, flag_enc[-32:-16]))
                    cand_data = cand_block + flag_enc[-16:]

                    dts.append(attempt(cand_data))

                value = sum(dts)
                if value > best_t:
                    best_t = value
                    best_guess = guess

            block.append(best_guess)

        blocks.append(block)
        flag_enc = flag_enc[:-16]
        p.success(f'{bytes(block[::-1]).hex()}')

flagbytes = b''.join(bytes(x[::-1]) for x in blocks[::-1])
flag = flagbytes[:-flagbytes[-1]].decode()
log.info('Flag: %s', flag)
"""
[+] Opening connection to localhost on port 50000: Done
[*] Flag encrypted: ccc02d1622137fff0f59a0100dded91aee57d10ecb3b823b979809f549ed958aebc5bc99e7f96af9839ed9ca4b25bbc3f82702d502510fc5ca7190620c809359
[+] Decrypting block 1: 40742e2e2e666973683f7d0505050505
[+] Decrypting block 2: 7572652d6f6d73657468696e672d6f75
[+] Decrypting block 3: 53534d7b69646b2d69276c6c5f666967
[*] Flag: SSM{idk-i'll_figure-omsething-ou@t...fish?}
[*] Closed connection to localhost port 50000
"""
