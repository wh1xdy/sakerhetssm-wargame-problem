from pwn import *

class Cracker:
    def __init__(self, bits, atts, send_func, recv_func):
        self.state = [None] * bits
        self.known_bits = 0
        self.bits = bits
        self.iter = 1
        self.send = send_func
        self.recv = recv_func
        self.atts = atts

        self.send(0)
        self.base_val = self.recv()

    def check_next(self):
        known = self._known
        addend = self.find_sum_bits_next()

        know_shift = self._diff_known(addend)
        self.send(addend)
        new_count = self.recv()
        self.iter += 1

        die = False
        changed_unknown = new_count - self.base_val - know_shift
        #if not sum(changed) == changed_unknown:
        #    print(f"{sum(changed), changed_unknown = }")
        #    print(f"{changed = }")
        #    print(f"{new_count = }")
        #    print(f"{self.base_val = }")
        #    print(f"{know_shift = }")
        #    print(f"{self.state = }")
        #    die = True

        #print(f"{changed_unknown = }")

        if changed_unknown == 1:
            self.state[-self.known_bits - 1] = 0
            self.known_bits += 1
        else:
            for idx in range(abs(changed_unknown) + 1):
                if self.known_bits + 1 > self.bits:
                    return
                #    raise ValueError("Procced modulus.", self.state)
                self.state[-self.known_bits - 1] = 1
                self.known_bits += 1
            else:
                self.state[-self.known_bits - 1] = 0
                self.known_bits += 1

        #print(f"{self.state = }")
        #if die:
        #    exit()

        return

    # Brute force from top to bottom until found number that
    # when added to sum known gives 1 in first unknown bit
    def find_sum_bits_next(self):
        if self.iter == 0:
            return None

        known = self._known()
        counter = 0
        try_add = 0
        bleng = lambda try_add: (self.iter * try_add + known).bit_length()
        while bleng(try_add) != self.known_bits + 1:
            counter += 1
            i = 0
            try_add = int(bin(counter)[2:].rjust(i, "0")[::-1], 2)
            while bleng(try_add) <= self.known_bits + 2:
                i += 1
                try_add = int(bin(counter)[2:].rjust(i, "0")[::-1], 2)

                if bleng(try_add) == self.known_bits + 1:
                    break
        
        assert bleng(try_add) == self.known_bits + 1, (bleng(try_add), self.known_bits + 1)
        return try_add

    # Compute the known number (lower bits)
    def _known(self):
        if self.known_bits == 0:
            known = []
        else:
            known = self.state[-self.known_bits:]
        assert not None in known, print(known)
        known = sum(a*(1 << b) for a, b in zip(known, range(self.known_bits)[::-1]))
        
        return known

    # Calculate how many bits were changed during computation
    def _diff_known(self, addend):
        #addend = list(map(int, list(bin(addend)[2:])))
        known = self._known()
        base = known.bit_count()

        new = known + addend * self.iter
        new_bits = new.bit_count()
        assert new.bit_length() == self.known_bits + 1, (new.bit_length(), self.known_bits + 1)

        return new_bits - base - 1

    # Loop until found all bits
    def crack(self):
        for _ in range(self.atts - 1):
            if self.known_bits >= self.bits:
                print(f"decoded")
                break
            else:
                self.check_next()
            
            print(f"decoded {self.known_bits / self.bits * 100}% of bits")

        #print(self.atts, self.iter)
        for _ in range(self.atts - self.iter):
            self.send(0)
            self.recv()
            self.iter += 1

        return self._known()

#context.log_level = "debug"
conn = process("./container/service.py")

send = lambda x: conn.sendline(str(x).encode())
recv = lambda: int(conn.recvline().decode())
"""
def recv():
    x = conn.recvline().decode().split()
    x0 = int(x[0])
    lsit = eval(x[1])

    return x0, lsit
"""

#send(0)
#conn.recvall()

cracker = Cracker(380, 200, send, recv)
x = cracker.crack()

send(x)
print(f"sent {bin(x)}")

conn.interactive()