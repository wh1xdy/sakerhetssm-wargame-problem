#include <stdint.h>

uint8_t process4(uint8_t x)
{
    return ~((x * 5) + 0x11);
}
