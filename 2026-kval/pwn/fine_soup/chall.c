#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

int main()
{
    setbuf(stdin, NULL);
    FILE *std = stderr;

    puts("Lets cook some fine soup!");

    while (1)
    {
        fprintf(std, "\n--- New Ingredient ---\n");
        fprintf(std, "Stir the pot (yes) > ");
        char switch_choice[4];
        scanf("%3s", switch_choice);
        if (strcmp(switch_choice, "yes") == 0)
        {
            if (std == stdout)
            {
                std = stderr;
            }
            else
            {
                std = stdout;
            }
        }

        fprintf(std, "Set heat level (low/high) > ");
        char write_type[5];
        scanf("%4s", write_type);
        if (strcmp(write_type, "low") && strcmp(write_type, "high"))
        {
            fprintf(std, "Invalid heat level!\n");
            continue;
        }

        fprintf(std, "Pour position (max 500cm) > ");
        uint64_t offset;
        scanf("%lu", &offset);

        if (offset > 500)
        {
            fprintf(std, "Invalid position!\n");
            continue;
        }

        fprintf(std, "Add ingredient (max 8kg) > ");
        char buf[8];
        read(0, buf, 8);
        if (strcmp(write_type, "low") == 0 && *(uint64_t *)buf <= 0x100)
        {
            uint64_t value = (uint64_t)(uintptr_t)std + *(uint64_t *)buf;
            memcpy((char *)std + offset, &value, 8);
        }
        else if (strcmp(write_type, "high") == 0)
        {
            memcpy((char *)std + offset, buf, 8);
        }
        else
        {
            fprintf(std, "Bad ingredient!\n");
        }
    }
}
