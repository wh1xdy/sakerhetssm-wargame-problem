#define _GNU_SOURCE
#include <limits.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int has_premium = 0;

#define FLAG_BUFFER_SIZE 256
#define INPUT_BUFFER_SIZE 256
#define RAND_BUFFER_SIZE 256

int get_input(char *input)
{
    char *inputptr = fgets(input, INPUT_BUFFER_SIZE - 1, stdin);
    if (!inputptr)
    {
        printf("Failed to read input\n");
        return 0;
    }
    input[strcspn(input, "\n")] = 0;

    return 1;
}

void action_rot13()
{
    puts("ROT-13");
    printf("Input: ");
    char input[INPUT_BUFFER_SIZE];
    if (!get_input(input))
    {
        return;
    }

    size_t inputlen = strlen(input);
    for (size_t i = 0; i < inputlen; i++)
    {
        input[i] = (input[i] + 13) % 256;
    }

    printf("Result: %s\n", input);
}

void action_flip_case()
{
    puts("Flip case");
    printf("Input: ");
    char input[INPUT_BUFFER_SIZE];
    if (!get_input(input))
    {
        return;
    }

    size_t inputlen = strlen(input);
    for (size_t i = 0; i < inputlen; i++)
    {
        input[i] ^= 0x20;
    }

    printf("Result: %s\n", input);
}

void action_memfrob()
{
    puts("Memfrob");
    printf("Input: ");
    char input[INPUT_BUFFER_SIZE];
    if (!get_input(input))
    {
        return;
    }

    size_t inputlen = strlen(input);
    memfrob(input, inputlen);

    printf("Result: %s\n", input);
}

void action_backwards()
{
    puts("Backwards");
    printf("Input: ");
    char input[INPUT_BUFFER_SIZE];
    if (!get_input(input))
    {
        return;
    }

    char result[256];
    size_t inputlen = strlen(input);
    for (size_t i = 0; i < inputlen; i++)
    {
        result[inputlen - i - 1] = input[i];
    }
    result[inputlen] = 0;

    printf("Result: %s\n", result);
}

int get_flag(char *flag)
{
    FILE *flagfile = fopen("flag.txt", "r");
    if (!flagfile)
    {
        perror("Failed to open flag. Please contact an administrator");
        return 0;
    }

    int num_read = fread(flag, sizeof(flag[0]), FLAG_BUFFER_SIZE - 1, flagfile);
    if (num_read == 0)
    {
        printf("Failed to read flag. Please contact an administrator\n");
        return 0;
    }

    int res = fclose(flagfile);
    if(res != 0) {
        perror("failed to close flag. Please contact an administrator");
        return 0;
    }

    return 1;
}

int get_random(char *buf)
{
    FILE *randfile = fopen("/dev/urandom", "r");
    if (!randfile)
    {
        perror("Failed to open /dev/urandom. Please contact an administrator");
        return 0;
    }

    int num_read = fread(buf, sizeof(buf[0]), RAND_BUFFER_SIZE - 1, randfile);
    if (num_read == 0)
    {
        printf("Failed to read random. Please contact an administrator\n");
        return 0;
    }

    int res = fclose(randfile);
    if(res != 0) {
        perror("failed to close /dev/urandom. Please contact an administrator");
        return 0;
    }

    return 1;
}

void action_enable_premium()
{
    puts("Enable premium");
    printf("Premium key: ");
    char input[INPUT_BUFFER_SIZE];
    if (!get_input(input))
    {
        return;
    }

    char flag[FLAG_BUFFER_SIZE];
    if (get_flag(flag) == 0)
    {
        return;
    }
    if (strcmp(flag, input) == 0)
    {
        puts("Valid key. Premium enabled");
        has_premium = 1;
    }
    else
    {
        puts("Invalid key. Premium not enabled");
    }

    return;
}

void action_xor_flag()
{
    puts("XOR with flag");
    char flag[FLAG_BUFFER_SIZE];
    if (get_flag(flag) == 0)
    {
        return;
    }

    printf("Input: ");
    char input[INPUT_BUFFER_SIZE];
    if (!get_input(input))
    {
        return;
    }

    size_t inputlen = strlen(input);
    size_t flaglen = strlen(flag);
    for (size_t i = 0; (i < inputlen) && (i < flaglen); i++)
    {
        input[i] ^= flag[i];
    }

    printf("Result: %s\n", input);
}

void action_one_time_pad()
{
    puts("XOR with one-time pad");
    printf("Input: ");
    char input[INPUT_BUFFER_SIZE];
    if (!get_input(input))
    {
        return;
    }

    char randbuf[RAND_BUFFER_SIZE];
    if (get_random(randbuf) == 0)
    {
        return;
    }

    size_t inputlen = strlen(input);
    for (size_t i = 0; i < inputlen; i++)
    {
        input[i] ^= randbuf[i];
    }

    printf("Result: %s\n", input);
}

void action_one_time_pad_and_flag()
{
    puts("XOR with flag and one-time pad");
    printf("Input: ");
    char input[INPUT_BUFFER_SIZE];
    if (!get_input(input))
    {
        return;
    }

    char flag[FLAG_BUFFER_SIZE];
    if (get_flag(flag) == 0)
    {
        return;
    }

    char randbuf[RAND_BUFFER_SIZE];
    if (get_random(randbuf) == 0)
    {
        return;
    }

    size_t inputlen = strlen(input);
    size_t flaglen = strlen(flag);
    for (size_t i = 0; i < inputlen && i < flaglen; i++)
    {
        input[i] ^= flag[i] ^ randbuf[i];
    }

    printf("Result: %s\n", input);
}

struct
{
    void (*premium_actions[5])();
    void (*regular_actions[5])();
} actions = {
    .premium_actions = {
        action_one_time_pad_and_flag,
        action_one_time_pad,
        action_xor_flag,
    },
    .regular_actions = {
        action_rot13,
        action_flip_case,
        action_memfrob,
        action_backwards,
        action_enable_premium,
    }};

const int num_regular_actions = (sizeof(actions.regular_actions) / sizeof(actions.regular_actions[0]));
const int num_premium_actions = (sizeof(actions.premium_actions) / sizeof(actions.premium_actions[0]));

int get_int(int *value)
{
    size_t linesize = 0;
    char *line = NULL;
    ssize_t res = getline(&line, &linesize, stdin);
    if (res == -1)
    {
        fprintf(stderr, "Failed to get line");
        *value = 0;
        return 0;
    }

    long int res2 = strtol(line, NULL, 10);
    if (res2 == LONG_MIN || res2 == LONG_MAX)
    {
        fprintf(stderr, "Failed to convert input to integer\n");
        *value = 0;
        return 0;
    }

    *value = res2;
    return 1;
}

void init()
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

void menu(int has_premium)
{
    puts("Welcome to the Premium Cryptor");
    if (has_premium)
    {
        puts("Premium: enabled");
    }
    else
    {
        puts("Premium: disabled");
    }
    puts("Please select your encryption method:");
    puts("");
    puts("Standard methods");
    puts("1. ROT-13");
    puts("2. Flip Case");
    puts("3. Memfrob");
    puts("4. Backwards");
    puts("5. Enable premium");
    puts("");
    puts("Premium methods");
    puts("6. XOR with one-time pad and flag");
    puts("7. XOR with one-time pad");
    puts("8. XOR with flag");
    puts("");
    printf("Choice: ");
}

int main()
{
    init();

    while (1)
    {
        menu(has_premium);
        int choice = 0;
        int res = get_int(&choice);
        if (res != 1)
        {
            fprintf(stderr, "Failed to get choice\n");
            return 1;
        }

        if (choice <= num_regular_actions)
        {
            int action_index = abs(choice - 1) % num_regular_actions;
            actions.regular_actions[action_index]();
        }
        else
        {
            if (has_premium)
            {
                int action_index = abs(choice - 5) % num_premium_actions;
                actions.premium_actions[action_index]();
            }
            else
            {
                puts("You do not have premium features enabled");
            }
        }
    }

    return 0;
}
