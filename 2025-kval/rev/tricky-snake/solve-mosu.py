


# unzipped code via cyberchef
"""

import builtins
import itertools

snek = b"\x48\x51\xf0\x0c\x44\xee\x39\xd9\x56\xfc\xa9\x9e\xbc\xf5\x9e\x0a\x7e\x17\xba\xeb\x07\x76\x1e\x37\x92\x80\x8d\x3c\x70\x48\xad\x4f"
orig_input = builtins.input
def input_tricky(key):
  value = orig_input(key)
  result = bytes(x ^ y for x,y in zip(value.encode(), itertools.cycle(snek)))
  return result.hex()
builtins.input = input_tricky


"""

target = "1b02bd772b8666b739a3c4e7e386ed791b74c88e73296d44e1f4ec4f033bc532"
target_bytes = result = bytes.fromhex(target)
snek = b"\x48\x51\xf0\x0c\x44\xee\x39\xd9\x56\xfc\xa9\x9e\xbc\xf5\x9e\x0a\x7e\x17\xba\xeb\x07\x76\x1e\x37\x92\x80\x8d\x3c\x70\x48\xad\x4f"

print(bytes(x ^ y for x,y in zip(target_bytes, snek)))
# output SSM{oh_no_my_sssecret_ssstasssh}
