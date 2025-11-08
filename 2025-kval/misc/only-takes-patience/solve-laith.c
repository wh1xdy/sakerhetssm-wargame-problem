#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int main()
{
	const char enc[] = {0x9d, 0xfa, 0xe6, 0x67, 0xf9, 0xc7, 0xd2, 0x4a, 0x2d, 0x6f, 0x8e, 0x15, 0x89, 0x55, 0x79, 0xf5, 0xc8, 0x33, 0x31, 0xe3, 0xdc, 0x2f, 0xc8, 0x4c};
	unsigned i = 1704067200; // 2024-01-01 00:00:00
	for (; i < UINT32_MAX; i++)
	{
		srand(i);
		char a = enc[0] ^ (rand() % 256),
			 b = enc[1] ^ (rand() % 256),
			 c = enc[2] ^ (rand() % 256),
			 d = enc[3] ^ (rand() % 256);

		if (a == 'S' && b == 'S' && c == 'M' && d == '{')
			break;
	}

	srand(i);
	for (int j = 0; j < sizeof(enc); j++)
		printf("%c", enc[j] ^ (rand() % 256));
	puts("");

	return 0;
}
