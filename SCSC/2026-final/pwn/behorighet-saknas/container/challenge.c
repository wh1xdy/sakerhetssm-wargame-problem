#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <openssl/evp.h>
#include <stdbool.h>

#define MAX_USERNAME 64
#define MAX_PASSWORD 128
#define FLAG_FILE "flag.txt"
#define HASH_SIZE 32

const char *mil_jargon[] = {
    "digitalisering och den globala strukturen bidrar till anonymitet.",
    "gig-ekonomin skapar en arena för uppdragsgivare att anonymt be om tjänster.",
    "mer avancerade cyberangrepp kan utföras i kombination med andra metoder och förmågor.",
    "mindre kvalificerade metoder används både av statsaktörer som av ideologiskt eller ekonomiskt motiverade aktörer.",
    "den geopolitiska och teknologiska utvecklingen bedöms påverka svensk ekonomisk säkerhet i ökande utsträckning."
};

void hash_password(char *password, int len) {
    unsigned char hash[HASH_SIZE];
    unsigned int hash_len;
    EVP_MD_CTX *mdctx;
    const EVP_MD *md;

    if (len < 0 || len > MAX_PASSWORD) {
        return;
    }

    md = EVP_sha256();
    mdctx = EVP_MD_CTX_new();

    if (mdctx == NULL) {
        fprintf(stderr, "Error initializing hash context\n");
        return;
    }

    EVP_DigestInit_ex(mdctx, md, NULL);
    EVP_DigestUpdate(mdctx, password, (size_t)len);
    EVP_DigestFinal_ex(mdctx, hash, &hash_len);
    EVP_MD_CTX_free(mdctx);

    memcpy(password, hash, HASH_SIZE);
}

void replace_chars(char* str, char old, char new, size_t len) {
    for (size_t i = 0; i < len; i++) {
        if (str[i] == old) {
            str[i] = new;
        }
    }
}

int read_password(char *buf, int max_len) {

    char tmp_buf[MAX_PASSWORD] = {0};
    fgets(tmp_buf, MAX_PASSWORD, stdin);
    size_t pw_len = strlen(tmp_buf);

    if (pw_len > 1) {
        replace_chars(tmp_buf, 0x0a, 0x00, pw_len);
        strcpy(buf, tmp_buf);
    }

    return strlen(buf);
}

int login(char *password) {
    FILE *fp;
    char correct_password[MAX_PASSWORD];
    int result1, result2;

    fp = fopen(FLAG_FILE, "r");
    if (fp == NULL) {
        fprintf(stderr, "Error: Could not open flag file\n");
        return 0;
    }

    if (fgets(correct_password, sizeof(correct_password), fp) == NULL) {
        fprintf(stderr, "Error: Could not read flag\n");
        fclose(fp);
        return 0;
    }

    correct_password[strcspn(correct_password, "\n")] = '\0';
    fclose(fp);

    result1 = strcmp(password, correct_password);
    if (result1 == 0) {
        return 1;
    }

    char other_password[MAX_PASSWORD] = {0};
    result2 = strcmp(password, other_password);
    if (result2 == 0) {
        return 1;
    }

    return 0;
}

int main() {
    char username[MAX_USERNAME] = " ";
    char password[MAX_PASSWORD] = " ";
    int login_attempts = 0;
    int urandom_fd;

    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);

    srand((unsigned int)time(NULL));

    printf("\nVänligen identifiera Er med korrekt och fullständigt auktoriseringsunderlag enligt gällande inloggningsprotokoll och säkerhetsföreskrifter, innan fortsatt åtkomst till det avsedda systemets digitala resurser beviljas.\n\n");

    while (true) {
        int count = sizeof(mil_jargon) / sizeof(mil_jargon[0]);
        int index = rand() % count;
        printf("\nDet är av största vikt att vi möter hoten mot vårt land med en samlad svensk ansats och tillsammans med våra allierade då %s\n\n", mil_jargon[index]);

        printf("Ange användarnamn: ");
        if (fgets(username, sizeof(username), stdin) == NULL) {
            fprintf(stderr, "Fel vid inläsning av användarnamn\n");
            return 1;
        }

        size_t newline_pos = strcspn(username, "\n");
        if (newline_pos < sizeof(username)) {
            username[newline_pos] = '\0';
        }

        printf("Ange lösenord: ");
        int pwd_len = read_password(password, sizeof(password));

        if (login(password)) {
            printf("Åtkomst beviljad. Ni har nu formellt tillträde till systemets tilldelade digitala domäner och funktionaliteter.\n");
            system("/bin/sh");
            break;
        }
        printf("Behörighet saknas!\n");
        sleep(1);
        login_attempts++;
        hash_password(password, pwd_len);
    }

    return 0;
}
