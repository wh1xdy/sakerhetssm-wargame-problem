#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

const char *program;

int stack[100];

unsigned char memory[30000];

int pc, sp, mi;

void default_exception_handler(const char *msg, void *dummy)
{
	(void) dummy;
	fprintf(stderr, "*** exception: ");
	puts(msg);
	fprintf(stderr, "*** exiting.\n");
	_Exit(1);
}

void (*exception_handler)(const char *, void *) = default_exception_handler;

void xwrite(int fd, const void *buf, ssize_t n)
{
	ssize_t ret = write(fd, buf, n);
	if (ret != n)
		exception_handler("write() syscall failed", NULL);
}

void xread(int fd, void *buf, ssize_t n)
{
	ssize_t ret = read(fd, buf, n);
	if (ret != n)
		exception_handler("read() syscall failed", NULL);
}

static void execute(char insn)
{
	switch(insn) {
	case '>':
		mi++;
		break;
	case '<':
		mi--;
		break;
	case '+':
		if (mi < 0 || mi >= 0x30000) exception_handler("out of bounds", NULL);
		memory[mi]++;
		break;
	case '-':
		if (mi < 0 || mi >= 0x30000) exception_handler("out of bounds", NULL);
		memory[mi]--;
		break;
	case '.':
		xwrite(STDOUT_FILENO, memory+mi, 1);
		break;
	case ',':
		xread(STDIN_FILENO, memory+mi, 1);
		break;
	case '[':
		if (mi < 0 || mi >= 0x30000) exception_handler("out of bounds", NULL);
		if (memory[mi] == 0) {
			int depth = 1;
			do {
				pc++;
				if (!program[pc]) _Exit(0);
				if (program[pc] == '[') depth++;
				if (program[pc] == ']') depth--;
			} while(depth);
			break;
		}
		stack[sp++] = pc;
		break;
	case ']':
		if (mi < 0 || mi >= 0x30000 || sp <= 0) exception_handler("out of bounds", NULL);
		if (memory[mi] == 0)
			sp--;
		else
			pc = stack[--sp] - 1; // decrement it because it is incremented in main
		break;
	case '@':
		exception_handler((const char *) memory + mi, NULL);
		break;
	case '0':
		_Exit(0);
	}
}

int main(int argc, char **argv)
{
	if (argc != 2) exception_handler("expected one argument", NULL);

	program = argv[1];

	for (;;) {
		char insn = program[pc];
		execute(insn);
		pc++;
	}
}

void bananas [[gnu::used]] (void)
{
	execl("/usr/bin/echo", "/usr/bin/echo", "bananas", NULL);
}


