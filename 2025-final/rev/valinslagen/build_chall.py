import os
from pwn import *
from tqdm import tqdm
from itertools import cycle

context.arch = 'amd64'
context.bits = 64

def pack(key, data):
    assert len(key) == 8
    unpacker = asm(f'''
    lea r14, [rip+loop_end]
    mov r15, {u64(key)}
    mov r13, {(len(data)+7)//8}

    loop_start:
    test r13, r13
    jz loop_end
    xor qword ptr [r14], r15
    add r14, 8 
    dec r13
    jmp loop_start
    loop_end:
    ''')
    if len(data)%8 != 0:
        data += b'\0'*(8-len(data)%8)
    enc = bytes([a^b for a, b in zip(data, cycle(key))])
    return unpacker + enc

flag = 'SSM{god_jul!(+-30dagar)}'.encode()

program = asm(f'''
jmp main
buffer:
    .fill {len(flag)}, 1, 0

main:
    mov rax, SYS_read
    mov rdi, 0
    lea rsi, [rip+buffer]
    mov rdx, {len(flag)}
    syscall
    lea rdi, [rip+buffer]
''')


checker_asm = '''
mov r13, 0
mov rax, 0
'''
for i, ch in enumerate(flag):
    checker_asm += f'''
    cmp byte ptr [rdi+{i}], {ch}
    setz al
    add r13, rax
'''

checker_asm += f'''
    cmp r13, {len(flag)}
    jne fail

    mov rax, SYS_write
    mov rdi, 0
    lea rsi, [rip+win_msg]
    mov rdx, win_msg_end-win_msg
    syscall

    mov rax, SYS_exit
    mov rdi, 1
    syscall

    fail:
    mov rax, SYS_write
    mov rdi, 0
    lea rsi, [rip+loser_msg]
    mov rdx, loser_msg_end-loser_msg
    syscall

    mov rax, SYS_exit
    mov rdi, 2
    syscall
    win_msg:
    .asciz "Bra jobbat!\\n\\0"
    win_msg_end:
    loser_msg:
    .asciz "Ajaj, det var fel!\\n\\0"
    loser_msg_end:
'''

checker = asm(checker_asm)
for _ in tqdm(range(0x80)): # number of layers
    checker = pack(os.urandom(8), checker)
program += checker

ELF.from_bytes(program).save('present')