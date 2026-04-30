#include <stdio.h>
#include <zlib.h>
#include <sys/mman.h>

int main() {
  printf("Send me your compressed shellcode:\n");
  fflush(stdout);
  char input[512];
  char *yolo = mmap(NULL, 4096, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

  z_stream strm = {0};
  deflateInit(&strm, Z_DEFAULT_COMPRESSION);
  strm.avail_in = read(0, input, sizeof(input));
  strm.next_in = input;
  strm.avail_out = 4096;
  strm.next_out = yolo;

  printf("This is how you decompress right?\n");
  fflush(stdout);
  deflate(&strm, Z_FINISH);

  deflateEnd(&strm);

  asm volatile("jmp *%[addr]"
    :
    : [addr] "m" (yolo)
    , "a" (0)
    , "c" (0)
    , "d" (0)
    , "b" (0)
    , "I" (0)
    , "S" (0)
  );

  __builtin_unreachable();
}
