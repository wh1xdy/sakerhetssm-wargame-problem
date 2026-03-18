#include <stdint.h>

uint8_t process2(uint8_t x)
{
    return (x ^ 0x3F) - 0x12;
}
