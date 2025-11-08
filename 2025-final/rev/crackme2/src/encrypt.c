unsigned char encrypt(unsigned char value, unsigned char index) {
    unsigned char result = value ^ index;
    result += 13;
    result ^= 37;
    return result;
}

int main(){}
