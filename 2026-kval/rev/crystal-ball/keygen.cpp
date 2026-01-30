#include <iostream>


#include "keygen.hpp"

constexpr const char* const flag = "SSM{I_see_3ndless_gl0ry}";
constexpr size_t flaglen = std::string::traits_type::length(flag);

int main() {
    uint8_t key[flaglen] = {0};
    uint8_t encrypted[flaglen] = {0};
    the_orb<0, 0, flaglen, 0>::observe(key);

    for(size_t i = 0; i < flaglen; i++) {
        encrypted[i] = flag[i] ^ key[i];
    }

    for (size_t  i = 0; i < flaglen; i++)
    {
        printf("%#x,", encrypted[i]);
    }
    puts("");

    return 0;
}
