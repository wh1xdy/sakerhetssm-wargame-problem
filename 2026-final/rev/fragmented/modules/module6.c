#include <stdint.h>

uint8_t process6(uint8_t x)
{
    return ((x + 23) ^ 0x55) * 7;
}
