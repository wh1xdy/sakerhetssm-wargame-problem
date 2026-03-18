#include <stdint.h>

uint8_t process7(uint8_t x)
{
    return (x * 0x81) ^ 0x0F;
}
