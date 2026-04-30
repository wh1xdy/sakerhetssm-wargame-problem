#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define MAX_KEYS 16
#define MAX_KEY_SIZE 0x100
#define MAX_NAME 0x40

typedef struct {
    int active;
    char name[MAX_NAME];
    size_t length;
    unsigned char *data;
} key_entry_t;

key_entry_t vault[MAX_KEYS];

void setup(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

int read_int(void) {
    char buf[16];
    if (!fgets(buf, sizeof(buf), stdin))
        exit(0);
    return atoi(buf);
}

void read_str(char *dst, int maxlen) {
    int i = 0;
    char c;
    while (i < maxlen - 1) {
        if (read(STDIN_FILENO, &c, 1) != 1)
            exit(0);
        if (c == '\n')
            break;
        dst[i++] = c;
    }
    dst[i] = '\0';
}

void fill_random(unsigned char *buf, size_t len) {
    FILE *f = fopen("/dev/urandom", "r");
    if (!f) {
        perror("urandom");
        exit(1);
    }
    fread(buf, 1, len, f);
    fclose(f);
}

void create_key(void) {
    int idx, len;
    unsigned char keybuf[MAX_KEY_SIZE];

    printf("Slot [0-%d]: ", MAX_KEYS - 1);
    idx = read_int();
    if (idx < 0 || idx >= MAX_KEYS) {
        puts("Invalid slot.");
        return;
    }
    if (vault[idx].active) {
        puts("Slot already in use.");
        return;
    }

    printf("Key name: ");
    read_str(vault[idx].name, MAX_NAME);

    printf("Key length: ");
    len = read_int();
    if (len <= 0 || (size_t)len > MAX_KEY_SIZE) {
        puts("Invalid length.");
        return;
    }

    vault[idx].data = malloc(len);
    if (!vault[idx].data) {
        puts("Allocation failed.");
        return;
    }
    vault[idx].length = len;
    vault[idx].active = 1;

    fill_random(keybuf, len);
    memcpy(vault[idx].data, keybuf, len);
    printf("Key generated in slot %d.\n", idx);
}

void view_key(void) {
    int idx;

    printf("Slot [0-%d]: ", MAX_KEYS - 1);
    idx = read_int();
    if (idx < 0 || idx >= MAX_KEYS) {
        puts("Invalid slot.");
        return;
    }
    if (!vault[idx].data) {
        puts("No key data.");
        return;
    }

    printf("Name: %s\nLength: %zu\nKey: \033[32m", vault[idx].name, vault[idx].length);
    size_t keylen = strlen(vault[idx].data);
    for (size_t i = 0; i < keylen; i++)
        printf("%02x", vault[idx].data[i]);
    printf("\033[0m\n");
}

void delete_key(void) {
    int idx;

    printf("Slot [0-%d]: ", MAX_KEYS - 1);
    idx = read_int();
    if (idx < 0 || idx >= MAX_KEYS) {
        puts("Invalid slot.");
        return;
    }
    if (!vault[idx].active) {
        puts("Slot not active.");
        return;
    }

    free(vault[idx].data);
    vault[idx].active = 0;
    printf("Key deleted from slot %d.\n", idx);
}

void regenerate_key(void) {
    int idx, len, mode;
    unsigned char keybuf[MAX_KEY_SIZE];

    printf("Slot [0-%d]: ", MAX_KEYS - 1);
    idx = read_int();
    if (idx < 0 || idx >= MAX_KEYS) {
        puts("Invalid slot.");
        return;
    }
    if (!vault[idx].active) {
        puts("Slot not active.");
        return;
    }

    printf("New key length: ");
    len = read_int();
    if (len <= 0 || (size_t)len > MAX_KEY_SIZE) {
        puts("Invalid length.");
        return;
    }

    printf("Mode [1=low 2=high 3=both]: ");
    mode = read_int();

    fill_random(keybuf, len);

    switch (mode) {
        case 1:
            for (int i = 0; i < len; i++)
                vault[idx].data[i] = (vault[idx].data[i] & 0xF0) | (keybuf[i] & 0x0F);
            break;
        case 2:
            for (int i = 0; i < len; i++)
                vault[idx].data[i] = (vault[idx].data[i] & 0x0F) | (keybuf[i] & 0xF0);
            break;
        default:
            memcpy(vault[idx].data, keybuf, len);
            break;
    }

    vault[idx].length = len;
    puts("Key regenerated.");
}

void vault_status(void) {
    int i, count = 0;

    for (i = 0; i < MAX_KEYS; i++)
        if (vault[i].active) count++;

    printf("Active keys: %d/%d\n", count, MAX_KEYS);
}

void menu(void) {
    puts("\n[1] Create key");
    puts("[2] View key");
    puts("[3] Delete key");
    puts("[4] Regenerate key");
    puts("[5] Vault status");
    puts("[6] Exit");
    printf("> ");
}

int main(void) {
    setup();

    puts("=== KeyVault v1.0 ===");
    puts("Secure Key Management\n");

    while (1) {
        menu();
        switch (read_int()) {
            case 1: create_key(); break;
            case 2: view_key(); break;
            case 3: delete_key(); break;
            case 4: regenerate_key(); break;
            case 5: vault_status(); break;
            case 6: puts("Goodbye."); return 0;
            default: puts("Invalid choice."); break;
        }
    }
}
