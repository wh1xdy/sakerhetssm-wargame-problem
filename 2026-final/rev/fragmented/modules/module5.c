#include <stdint.h>

uint8_t process5(uint8_t x)
{
    return ((x >> 4) | (x << 4)) + 0x80;
}
