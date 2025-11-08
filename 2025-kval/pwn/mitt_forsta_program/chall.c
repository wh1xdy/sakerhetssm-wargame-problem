#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/sendfile.h>
#include <sys/stat.h>
#include <fcntl.h>

void win() {
    struct stat st;
    int fd = open("flag.txt", O_RDONLY);
    fstat(fd, &st);
    sendfile(1, fd, NULL, st.st_size);
    exit(0);
}

int main() {
    char name[100];

    setvbuf(stdout, NULL, _IONBF, 0); // Disable output buffering
    setvbuf(stdin, NULL, _IONBF, 0); // Disable input buffering

    puts("Välkommen till mitt första program! Vad heter du?");
    fgets(name, 0x100, stdin);
    name[strcspn(name, "\n")] = 0;
    printf("Hej %s! Hoppas du har en bra dag!!!\n", name);

    return 0;
}
