#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "han.h"
#include "handler.h"

#define MAX_PARAMS      16
#define PARAM_NAME_MAX  32
#define PARAM_VALUE_MAX 64

typedef struct {
    char name[PARAM_NAME_MAX];
    char value[PARAM_VALUE_MAX];
} param_t;

static param_t params[MAX_PARAMS];
static int     param_count = 0;
static char    meter_alias[64] = "";
static char    flag_snippet[256] = "";

void init_flag_snippet(const char *s)
{
    strncpy(flag_snippet, s, sizeof(flag_snippet) - 1);
    flag_snippet[sizeof(flag_snippet) - 1] = '\0';
}

void print_flag_snippet(void)
{
    printf("Meter secret: %s\n", flag_snippet);
    fflush(stdout);
    exit(0);
}

/* SET_PARAM <name> <value> */
static void handle_set_param(const char *args)
{
    /* find the space separating name from value */
    const char *sp = strchr(args, ' ');
    if (!sp) {
        puts("Usage: SET_PARAM <name> <value>");
        return;
    }

    /* safe name copy: bounded by PARAM_NAME_MAX */
    size_t nlen = (size_t)(sp - args);
    if (nlen == 0 || nlen >= PARAM_NAME_MAX) {
        puts("Error: invalid parameter name");
        return;
    }

    char value[PARAM_VALUE_MAX];
    strcpy(value, sp + 1);

    /* store in params table, reusing existing slot if name matches */
    for (int i = 0; i < param_count; i++) {
        if (memcmp(params[i].name, args, nlen) == 0 &&
                params[i].name[nlen] == '\0') {
            memcpy(params[i].value, value, PARAM_VALUE_MAX);
            puts("OK");
            return;
        }
    }
    if (param_count < MAX_PARAMS) {
        memcpy(params[param_count].name, args, nlen);
        params[param_count].name[nlen] = '\0';
        memcpy(params[param_count].value, value, PARAM_VALUE_MAX);
        param_count++;
    }
    puts("OK");
}

static void handle_get_param(const char *args)
{
    for (int i = 0; i < param_count; i++) {
        if (strcmp(params[i].name, args) == 0) {
            printf("%s\n", params[i].value);
            return;
        }
    }
    puts("(not set)");
}

static void handle_list_params(void)
{
    if (param_count == 0) {
        puts("(empty)");
        return;
    }
    for (int i = 0; i < param_count; i++) {
        printf("%-*s  %s\n", PARAM_NAME_MAX - 1,
               params[i].name, params[i].value);
    }
}

static void handle_reset_params(void)
{
    memset(params, 0, sizeof(params));
    param_count = 0;
    puts("OK");
}

static void handle_info(han_port_t *port)
{
    printf("Meter-ID:   %s\n", port->meter_id);
    printf("Name:       %s\n", port->name);
    printf("Alias:      %s\n", meter_alias[0] ? meter_alias : "(none)");
    printf("PID:        %d\n", (int)getpid());
    printf("Firmware:   HAN-SIM/1.0\n");
    printf("Protocol:   DSMR P1 v5.0\n");
    printf("Params:     %d/%d\n", param_count, MAX_PARAMS);
}

static void handle_rename(const char *args)
{
    strncpy(meter_alias, args, sizeof(meter_alias) - 1);
    meter_alias[sizeof(meter_alias) - 1] = '\0';
    puts("OK");
}

static void handle_ping(void)
{
    puts("PONG");
}

static void handle_help(void)
{
    puts("Available commands:");
    puts("  PING                   Check connection; replies PONG");
    puts("  INFO                   Show meter identity and status");
    puts("  RENAME <alias>         Set a human-readable alias for this meter");
    puts("  SET_PARAM <name> <val> Store a named parameter");
    puts("  GET_PARAM <name>       Retrieve a stored parameter");
    puts("  LIST_PARAMS            List all stored parameters");
    puts("  RESET_PARAMS           Clear all stored parameters");
    puts("  HELP                   Show this help text");
}

void meter_handler(han_port_t *port, const char *cmd)
{
    /* skip leading whitespace */
    while (*cmd == ' ' || *cmd == '\t') cmd++;

/* compare verb (case-sensitive, space or NUL terminates verb) */
#define VERB(s) (strncmp(cmd, (s), sizeof(s) - 1) == 0 && \
                 (cmd[sizeof(s) - 1] == ' ' || cmd[sizeof(s) - 1] == '\0'))

    if (VERB("PING")) {
        handle_ping();
    } else if (VERB("INFO")) {
        handle_info(port);
    } else if (VERB("HELP")) {
        handle_help();
    } else if (VERB("RESET_PARAMS")) {
        handle_reset_params();
    } else if (VERB("LIST_PARAMS")) {
        handle_list_params();
    } else if (VERB("RENAME")) {
        const char *args = cmd + sizeof("RENAME") - 1;
        while (*args == ' ') args++;
        handle_rename(args);
    } else if (VERB("SET_PARAM")) {
        const char *args = cmd + sizeof("SET_PARAM") - 1;
        while (*args == ' ') args++;
        handle_set_param(args);
    } else if (VERB("GET_PARAM")) {
        const char *args = cmd + sizeof("GET_PARAM") - 1;
        while (*args == ' ') args++;
        handle_get_param(args);
    } else {
        puts("Unknown command. Try HELP.");
    }

    /* Sentinel: signals end of response to parent's port_send reader. */
    puts(".");

#undef VERB
}
