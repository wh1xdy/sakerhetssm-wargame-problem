#include <stdio.h>
#include <time.h>
#include <stdlib.h>

int get_random_num() {
	return rand() % 70000 + 70000;
}

void echo() {
	char input[32];
	scanf("%31s", input);
	printf("%s\n", input);
}

void spawn_shell() {
	printf("To get a shell you must answer the following question:\n");
	int a = get_random_num();
	int b = get_random_num();
	printf("What is %d + %d? \n", a, b);

	int input;
	scanf("%hu", &input);
	printf("You entered %d, the right answer is %d\n", input, a+b);
	if(a+b == input) {
		system("/bin/sh");
	}
}

int main() {
	setvbuf(stdout, 0, 2, 0);
	setvbuf(stdin, 0, 2, 0);

	srand((int)time(NULL));
	printf(" _____                              _ _     _      _\n");
	printf("|_   _|                            (_) |   | |    | |\n");
	printf("  | | _ __ ___  _ __   ___  ___ ___ _| |__ | | ___| |\n");
	printf("  | || '_ ` _ \\| '_ \\ / _ \\/ __/ __| | '_ \\| |/ _ \\ |\n");
	printf(" _| || | | | | | |_) | (_) \\__ \\__ \\ | |_) | |  __/_|\n");
	printf(" \\___/_| |_| |_| .__/ \\___/|___/___/_|_.__/|_|\\___(_)\n");
	printf("               | |\n");
	printf("               |_|\n");

	printf("Pick something to do:\n");
	printf("1) echo\n");
	printf("2) get a shell\n");
	printf("3) quit\n");

	int option=0;
	while(option != 3 && scanf("%d", &option) > 0) {
		switch(option) {
			case 1:
				echo();
				break;
			case 2:
				spawn_shell();
				break;
			default:
				break;
		}
	}

	return 0;
}
