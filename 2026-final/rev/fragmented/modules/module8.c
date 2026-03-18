#include <stdint.h>

uint8_t process8(uint8_t x)
{
    return (x + (x << 1)) ^ 0xCC;
}
