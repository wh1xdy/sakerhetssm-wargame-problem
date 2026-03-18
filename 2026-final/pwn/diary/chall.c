#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define MAX_ENTRIES 8
#define MAX_SIZE 0x1337

static char *entries[MAX_ENTRIES];
static size_t entry_sizes[MAX_ENTRIES];
static int in_use[MAX_ENTRIES];

static void setup(void) {
    puts("welcome to your diary");
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

static void die(void) {
    puts("that was, like, not the vibe");
    exit(1);
}

static long read_long(void) {
    char buf[32];

    if (fgets(buf, sizeof(buf), stdin) == NULL) {
        die();
    }
    buf[strcspn(buf, "\n")] = '\0';
    return strtol(buf, NULL, 10);
}

static int read_index(void) {
    puts("page number:");
    long idx = read_long();
    if (idx < 0 || idx >= MAX_ENTRIES) {
        puts("that page does not exist, bestie");
        return -1;
    }
    return (int)idx;
}

static void write_entry(void) {
    int idx;
    long size;

    idx = read_index();
    if (idx < 0) {
        return;
    }

    if (in_use[idx]) {
        puts("that page is already serving");
        return;
    }

    puts("how many letters?");
    size = read_long();
    if (size <= 0 || size > MAX_SIZE) {
        puts("too much drama for one page");
        return;
    }

    entries[idx] = malloc((size_t)size);
    if (entries[idx] == NULL) {
        die();
    }

    in_use[idx] = 1;
    entry_sizes[idx] = (size_t)size;
    puts("spill the tea:");
    if (read(STDIN_FILENO, entries[idx], entry_sizes[idx]) <= 0) {
        die();
    }
    puts("entry written");
}

static void tear_out_page(void) {
    int idx;

    idx = read_index();
    if (idx < 0) {
        return;
    }

    if (entries[idx] == NULL) {
        puts("that page is totally blank");
        return;
    }

    free(entries[idx]);
    in_use[idx] = 0;
    puts("page torn out");
}

static void read_diary(void) {
    int idx;

    idx = read_index();
    if (idx < 0) {
        return;
    }

    if (entries[idx] == NULL) {
        puts("that page is totally blank");
        return;
    }

    puts("dear diary...");
    write(STDOUT_FILENO, entries[idx], entry_sizes[idx]);
    puts("");
}

static void edit_entry(void) {
    int idx;

    idx = read_index();
    if (idx < 0) {
        return;
    }

    if (entries[idx] == NULL) {
        puts("that page is totally blank");
        return;
    }

    puts("rewrite the tea:");
    if (read(STDIN_FILENO, entries[idx], entry_sizes[idx]) <= 0) {
        die();
    }
    puts("entry refreshed");
}

int main(void) {
    long choice;

    setup();

    for (;;) {
        puts("");
        puts("1. write entry");
        puts("2. tear out page");
        puts("3. read diary");
        puts("4. edit entry");
        puts("5. close the diary");
        puts("pick a vibe:");

        choice = read_long();
        switch (choice) {
        case 1:
            write_entry();
            break;
        case 2:
            tear_out_page();
            break;
        case 3:
            read_diary();
            break;
        case 4:
            edit_entry();
            break;
        case 5:
            return 0;
        default:
            puts("that choice is not on the mood board");
            break;
        }
    }
}
