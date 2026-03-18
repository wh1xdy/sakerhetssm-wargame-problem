#include <stdint.h>

uint8_t process3(uint8_t x)
{
    return ((x << 3) | (x >> 5)) ^ 0xAA;
}
