#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    char name[100];

    setvbuf(stdout, NULL, _IONBF, 0); // Disable output buffering
    setvbuf(stdin, NULL, _IONBF, 0); // Disable input buffering

    printf("Välkommen till mitt andra program! Mitt tur-tal idag är %p. Vad heter du?\n", system);
    fgets(name, 0x100, stdin);
    name[strcspn(name, "\n")] = 0;
    printf("Hej %s! Hoppas du har en bra dag!!!\n", name);
    return 0;
}
