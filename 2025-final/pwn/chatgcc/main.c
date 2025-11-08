#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <string.h>
#include <time.h>

#define READ_END 0
#define WRITE_END 1

void read_input(char* buf, size_t size) {
    int i = 0;
    while (i < size - 1) {
        char c = getchar();
        if (c == '\n') {
            if (i > 0 && buf[i - 1] == '\n') {
                break;
            }
        }
        buf[i++] = c;
    }
    buf[i] = '\0';
}

int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);

    printf("Welcome to ChatGCC, what can I help you with?\n");
    printf("End each message with two newlines!\n");
    char chat[0x100];
    while (1) {
        printf(">> ");
        read_input(chat, sizeof(chat));

        if (strpbrk(chat, "#\\") != NULL) {
            printf("Sorry, I can't help you with that.\n");
            continue;
        }
        if (strstr(chat, "include") != NULL) {
            printf("Sorry, I can't help you with that.\n");
            continue;
        }

        int input[2], output[2];
        pipe(input);
        pipe(output);
        
        pid_t pid = fork();
        if (pid == 0) {
            char* argv[] = {"gcc", "-x", "c", "-E", "-trigraphs", "-o", "/dev/fd/1", "-", NULL};
            close(input[WRITE_END]);
            close(output[READ_END]);
            dup2(input[READ_END], STDIN_FILENO);
            dup2(output[WRITE_END], STDOUT_FILENO);
            execvp("gcc", argv);
            exit(0);
        } else {
            close(output[WRITE_END]);
            close(input[READ_END]);
            write(input[WRITE_END], chat, strlen(chat));
            close(input[WRITE_END]);
            waitpid(pid, NULL, 0);
            while (1) {
                char c;
                if (read(output[READ_END], &c, 1) == 0) {
                    break;
                }
                printf("%c", c);
                
                nanosleep((struct timespec[]){{0, 30000000}}, NULL);
            }
        }
    }
    return 0;
}