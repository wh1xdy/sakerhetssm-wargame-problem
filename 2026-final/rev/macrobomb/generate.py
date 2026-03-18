count = 16
macro_len = 197
# count = 4
# macro_len = 46
flag_len = 45
import random

main = open(f"main.c", "w")
macros = open(f"macros.h", "w")

main.write(f"""#include <stdio.h>
#include "macros.h"

char flag[{flag_len + 1}] = "";""" + "\n")

init = "".join(f"int db{i+1}; " for i in range(count))
macros.write(init + "\n")

random.seed(1230283759)

ends = init = "\n".join(f"#define end{i+1} flag[{i}]--" for i in range(flag_len))
macros.write(ends + "\n")

def get():
    rand = random.randrange(count+1)
    out = ""
    if rand == 0:
        rand = random.randrange(flag_len)
        out += f"end{rand+1}"
    else:
        out += f"db{rand}"

    return out

for macro_count in range(count):
    macro = f"#define db{macro_count+1}"
    for i in range(macro_len):
        macro += f" {get()};"
    macros.write(macro + "\n")

expand = "#define EXPAND() do {"
for i in range(count):
    expand += f" db{i+1};"
expand += " } while (0)"
macros.write(expand + "\n")

main.write("""
int main() {
    EXPAND();

    printf("%s\\n", flag);
    return 0;
}""" + "\n")
