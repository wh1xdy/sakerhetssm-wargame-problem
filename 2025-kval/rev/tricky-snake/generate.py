#!/usr/bin/env python3

import io
import secrets
import sys
import zipfile

outfile = sys.argv[1]
flag = sys.argv[2]

key = secrets.token_bytes(len(flag))
key_hex = ''.join(f'\\x{x:02x}' for x in key)
target = bytes(x^y for x,y in zip(flag.encode(), key))

backdoor = """
import builtins
import itertools

snek = b"%s"
orig_input = builtins.input
def input_tricky(key):
  value = orig_input(key)
  result = bytes(x ^ y for x,y in zip(value.encode(), itertools.cycle(snek)))
  return result.hex()
builtins.input = input_tricky
""" % key_hex

zip = io.BytesIO()
with zipfile.ZipFile(zip, mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as fzip:
    fzip.writestr('__main__.py', backdoor)

zip.seek(0)
zipdata = zip.getvalue()
ziphex = ''.join(f'\\x{x:02x}' for x in zipdata)

tricky_template = """
#!/usr/bin/env python3
__import__("runpy").run_path(__import__("py_compile").compile(__file__))



your_password = input("What issss the passssssword? ")
target = "%s"
if your_password == target:
  print("Correct! Congratulationsssss!")
else:
  print("Wrong!")








unused = b"%s"
"""

with open(outfile, 'w') as fout:
    fout.write(tricky_template % (target.hex(), ziphex))