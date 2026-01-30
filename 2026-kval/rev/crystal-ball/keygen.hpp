#include <cstdint>
#include <cstdio>
#include <cstdlib>

#include <sys/ptrace.h>

constexpr uint32_t constrand(uint32_t val)
{
    return ((val * 1103515245) + 12345) & 0x7fffffff;
}

template <int OP, int IDX, int LEN, int VAL>
class the_orb
{
public:
    static void observe(uint8_t *buffer);
};

template <int OP, int IDX, int LEN, int VAL>
void fork(uint8_t *buffer)
{
    constexpr uint32_t a = constrand(VAL);
    constexpr uint32_t b = constrand(a);
    constexpr uint32_t c = constrand(b);
    constexpr uint32_t d = constrand(c);
    constexpr uint32_t e = constrand(d);
    constexpr uint32_t f = constrand(e);
    constexpr uint32_t g = constrand(f);

    // printf("%d\n", g);

    if (IDX + 1 < LEN && (g >> 0) & 1)
        the_orb<d % 4, (IDX + 1) % LEN, LEN, a & 0xFF>::observe(buffer);
    if (IDX + 1 < LEN && (g >> 1) & 1)
        the_orb<e % 4, (IDX + 1) % LEN, LEN, b & 0xFF>::observe(buffer);
    if (IDX + 1 < LEN && (g >> 2) & 1)
        the_orb<f % 4, (IDX + 1) % LEN, LEN, c & 0xFF>::observe(buffer);
    if (IDX + 1 < LEN && (g >> 3) & 1)
        the_orb<f % 4, (IDX + 1) % LEN, LEN, c & 0xFF>::observe(buffer);
}

template <int IDX, int LEN, int VAL>
class the_orb<0, IDX, LEN, VAL>
{
public:
    static void observe(uint8_t *buffer)
    {
        buffer[IDX] += VAL;
        fork<0, IDX, LEN, VAL>(buffer);
    }
};

template <int IDX, int LEN, int VAL>
class the_orb<1, IDX, LEN, VAL>
{
public:
    static void observe(uint8_t *buffer)
    {
        buffer[IDX] -= VAL;
        fork<1, IDX, LEN, VAL>(buffer);
    }
};

template <int IDX, int LEN, int VAL>
class the_orb<2, IDX, LEN, VAL>
{
public:
    static void observe(uint8_t *buffer)
    {
        buffer[IDX] ^= VAL;
        fork<2, IDX, LEN, VAL>(buffer);
    }
};

template <int IDX, int LEN, int VAL>
class the_orb<3, IDX, LEN, VAL>
{
public:
    static void observe(uint8_t *buffer)
    {
        buffer[IDX] *= VAL;
        fork<3, IDX, LEN, VAL>(buffer);
    }
};

template <int LEN>
class the_orb<0, 15, LEN, 81>
{
public:
    static void observe(uint8_t *buffer)
    {
        if (!vision)
        {
            if (ptrace(PTRACE_TRACEME, 0, 1, 0) < 0)
            {
                puts("Oh no. Do not peer into the inner core of the orb. This is ill-advised");
                exit(1);
            }
            vision = true;
            puts("A vision is forming");
        }
        fork<0, 15, LEN, 82>(buffer);
    }

private:
    static bool vision;
};

template <int LEN>
bool the_orb<0, 15, LEN, 81>::vision = false;
