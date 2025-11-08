#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#include "flag.h"

int main(void)
{
	const char flag[] = FLAG;
	srand(time(NULL));
	for (int i = 0; i < sizeof(flag); i++)
	    printf("%x", flag[i] ^ (rand() % 256));
	puts("");

	return 0;
}
