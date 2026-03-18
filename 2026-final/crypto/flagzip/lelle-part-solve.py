#!/usr/bin/env python

from pwn import remote, process
from string import printable

printable = printable.replace("\n", "").replace("\r", "")
printable = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}'

num_requests = 0


class IO:
    def __init__(self):
        self.conn = process("./container/service")
        self.conn.recvlines(6)

    def io(self, msg: str) -> int:
        global num_requests
        num_requests += 1
        self.conn.sendline(msg.encode())
        cip = self.conn.recvline().split(b"your ciphertext: ")[1].decode()
        return len(bytes.fromhex(cip))

    def batch(self, msgs: list[str]) -> list[int]:
        global num_requests
        num_requests += 1
        self.conn.sendline(b"\n".join(msg.encode() for msg in msgs))
        cips = self.conn.recvlines(len(msgs))
        cips = map(lambda x: len(bytes.fromhex(
            x.split(b"your ciphertext: ")[1].decode())), cips)
        return cips


conn = IO()

counter = 0


def dfs(state, len, flag_len) -> tuple[bool, str]:
    global counter

    if len >= flag_len:
        return (False, state)

    msgs = [state + c for c in printable]
    batched = conn.batch(msgs)
    for msg, leng in zip(msgs, batched):
        # for c2 in printable:
        if msg == "SSM{psDI6Fz9iw9x}":
            return (True, msg)
        # leng = conn.io(state + char)
        if leng <= len + 1:
            if counter & 0xF == 0:
                print(leng, msg)
            if msg.endswith("}"):
                print(leng, msg)
            counter += 1
            valid, flag = dfs(msg, len, flag_len)
            if valid:
                return (valid, flag)
    else:
        return (False, "")


flag = "SSM{"
base = conn.io(flag)
print("base =", base)

dfs(flag, base, 74)
print(num_requests)
