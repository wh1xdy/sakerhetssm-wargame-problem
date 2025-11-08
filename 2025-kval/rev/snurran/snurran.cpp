#include <stdlib.h>
#include <sys/syscall.h>

#include <stdio.h>
#include <string.h>

struct String {
  char val;
  String *next;
};

char getch() {
  char buffer;
  ssize_t bytes_read;

  // Make a direct syscall (SYS_read) to read 1 byte from stdin (fd 0)
  __asm__ volatile (
      "syscall"                    // Invoke the syscall instruction
      : "=a" (bytes_read)           // Output: syscall return value goes to 'bytes_read'
      : "a" (SYS_read),             // Input: syscall number (0 for sys_read)
      "D" (0),                    // File descriptor (0 = stdin)
      "S" (&buffer),              // Buffer to store the result
      "d" (1)                     // Number of bytes to read (1 byte)
      : "rcx", "r11", "memory"      // Clobbered registers
      );

  return buffer;
}

#define flaglen 20

int main() {
  String *first = (String*) malloc(sizeof(String));
  first->val = getch();
  String *at = first;
  for (int i = 1; i < flaglen; i++) {
    String *next = (String*) malloc(sizeof(String));
    next->val = getch();
    at->next = next;
    at = next;
  }
  at->next = first;
  first = at = NULL;
  abort();
  printf("first: %c\n", first->val);
}
