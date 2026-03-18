#include <stdio.h>
#include "macros.h"

char flag[46] = "\xf3g\x81\x05%,\xca'\x17+\xa7\xfd\nS\xacT[\x00\x8d\xc1\x96@&\xb8Qu\xcefc\x19Ye\xef\xef-\xbf\xd0\xc8\xc7i'o\xe5Bg";

int main() {
    EXPAND();

    printf("%s\n", flag);
    return 0;
}
