#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

uint8_t process1(uint8_t x);
uint8_t process2(uint8_t x);
uint8_t process3(uint8_t x);
uint8_t process4(uint8_t x);
uint8_t process5(uint8_t x);
uint8_t process6(uint8_t x);
uint8_t process7(uint8_t x);
uint8_t process8(uint8_t x);

typedef uint8_t (*transform_func_t)(uint8_t);

transform_func_t processors[] = {
    process1,
    process2,
    process3,
    process4,
    process5,
    process6,
    process7,
    process8
};

int main(int argc, char** argv) {
    if(argc < 2) {
        printf("Usage %s: <flag>\n", argv[0]);
        return 1;
    }
    char* flag = argv[1];

    size_t flaglen = strlen(flag);
    for(size_t i = 0; i < flaglen; i++) {
        uint8_t res = processors[i % (sizeof(processors)/sizeof(processors[0]))](flag[i]);
        printf("%02x", res);
    }
    printf("\n");
}
