#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/bn.h>
#include <openssl/crypto.h>

unsigned char n[0x100] = "\xde\xad\xbe\xef";
unsigned char e[0x10] = "\x03";
unsigned char command[0x10] = "openssl version";

int readint()
{
    char buf[0x10];
    fgets(buf, sizeof(buf), stdin);
    return atoi(buf);
}

void status()
{
    system(command);
}

void menu()
{
    printf("1. Set RSA Params \n");
    printf("2. Encrypt \n");
    printf("3. Check openssl version\n");
    printf("4. Exit\n");
}

void set_params()
{
    BN_CTX *ctx = BN_CTX_new();

    printf("e: ");
    char e_str[0x10];
    fgets(e_str, sizeof(e_str), stdin);

    BIGNUM *big_e = BN_new();
    BN_dec2bn(&big_e, e_str);
    memset(e, 0, sizeof(e));
    BN_bn2bin(big_e, e);

    printf("p: ");
    char p_str[0x150];
    fgets(p_str, sizeof(p_str), stdin);

    BIGNUM *p = BN_new();
    BN_dec2bn(&p, p_str);

    printf("q: ");
    char q_str[0x150];
    fgets(q_str, sizeof(q_str), stdin);

    BIGNUM *q = BN_new();
    BN_dec2bn(&q, q_str);

    BIGNUM *big_n = BN_new();
    BN_mul(big_n, p, q, ctx);

    memset(n, 0, sizeof(n));
    BN_bn2bin(big_n, n);

    BN_free(big_e);
    BN_free(p);
    BN_free(q);
    BN_free(big_n);
    BN_CTX_free(ctx);
}

void encrypt()
{
    BN_CTX *ctx = BN_CTX_new();

    printf("pt: ");
    char pt_str[0x100];
    fgets(pt_str, sizeof(pt_str), stdin);

    BIGNUM *pt = BN_new();
    BN_dec2bn(&pt, pt_str);

    BIGNUM *big_e = BN_new();
    BN_bin2bn(e, sizeof(e), big_e);

    BIGNUM *big_n = BN_new();
    BN_bin2bn(n, sizeof(n), big_n);

    BIGNUM *c = BN_new();
    BN_mod_exp(c, pt, big_e, big_n, ctx);

    char *ct_str = BN_bn2dec(c);
    printf("ct: %s\n", ct_str);
    OPENSSL_free(ct_str);

    BN_free(pt);
    BN_free(big_e);
    BN_free(big_n);
    BN_free(c);
    BN_CTX_free(ctx);
}

int main()
{
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);

    while (1)
    {
        menu();

        printf("> ");
        int num = readint();

        if (num == 1)
        {
            set_params();
        }
        else if (num == 2)
        {
            encrypt();
        }
        else if (num == 3)
        {
            status();
        }
        else if (num == 4)
        {
            exit(0);
        }
        else
        {
            printf("Invalid choice\n");
        }
    }
}
