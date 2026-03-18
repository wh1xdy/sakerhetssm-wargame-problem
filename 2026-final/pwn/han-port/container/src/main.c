#define _POSIX_C_SOURCE 200809L

#include <math.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "han.h"
#include "port_proc.h"
#include "ports.h"

/* ------------------------------------------------------------------ */

static void print_help(void)
{
    puts("Commands:");
    puts("  list           list available HAN ports");
    puts("  select <n>     connect to port number <n>");
    puts("  read           read current telegram from selected port");
    puts("  send <cmd>     send command string to selected port handler");
    puts("  help           show this help");
    puts("  quit           exit");
}

static void cmd_list(void)
{
    printf(" %-4s  %-20s  %-12s  %s\n",
           "ID", "Name", "Meter ID", "Location");
    printf(" %-4s  %-20s  %-12s  %s\n",
           "----", "--------------------", "------------", "--------------------");

    for (int i = 0; i < port_count; i++) {
        char loc[32];
        snprintf(loc, sizeof(loc), "%.4f\xc2\xb0%c, %.4f\xc2\xb0%c",
                 fabs(ports[i].location.lat),
                 ports[i].location.lat >= 0.0 ? 'N' : 'S',
                 fabs(ports[i].location.lon),
                 ports[i].location.lon >= 0.0 ? 'E' : 'W');
        printf(" %-4d  %-20s  %-12s  %s\n",
               i, ports[i].name, ports[i].meter_id, loc);
    }
}

static void cmd_select(int *selected, const char *arg)
{
    if (!arg || !*arg) {
        puts("Usage: select <n>");
        return;
    }

    char *end;
    long n = strtol(arg, &end, 10);
    if (*end != '\0' || n < 0 || n >= port_count) {
        fprintf(stderr, "Invalid port index '%s' (valid range: 0-%d)\n",
                arg, port_count - 1);
        return;
    }

    *selected = (int)n;
    printf("Connected to %s  [%s]  %.4f\xc2\xb0%c, %.4f\xc2\xb0%c\n",
           ports[*selected].name,
           ports[*selected].meter_id,
           fabs(ports[*selected].location.lat),
           ports[*selected].location.lat >= 0.0 ? 'N' : 'S',
           fabs(ports[*selected].location.lon),
           ports[*selected].location.lon >= 0.0 ? 'E' : 'W');
}

static void cmd_read(port_proc_t *procs, int selected)
{
    if (selected < 0) {
        puts("No port selected. Use 'select <n>' first.");
        return;
    }
    port_read(&procs[selected]);
}

static void cmd_send(port_proc_t *procs, int selected, const char *cmd)
{
    if (selected < 0) {
        puts("No port selected. Use 'select <n>' first.");
        return;
    }
    if (!cmd || !*cmd) {
        puts("Usage: send <cmd>");
        return;
    }
    port_send(&procs[selected], cmd);
}

/* ------------------------------------------------------------------ */

int main(void)
{
    /* Ignore SIGPIPE so the parent survives writing to a dead child's pipe
     * (happens when a port process has been exploited and exited). */
    signal(SIGPIPE, SIG_IGN);

    port_proc_t *procs   = spawn_ports();

    /* Split the flag into one slice per port and deliver via INIT.
     * Afterwards scrub the flag from this (parent) process's memory. */
    char   flag_buf[] = FLAG;
    size_t flen       = strlen(flag_buf);
    for (int i = 0; i < port_count; i++) {
        size_t start = (flen * (size_t)i)       / (size_t)port_count;
        size_t end   = (flen * (size_t)(i + 1)) / (size_t)port_count;
        char snippet[256];
        size_t slen = end - start;
        memcpy(snippet, flag_buf + start, slen);
        snippet[slen] = '\0';
        port_init(&procs[i], snippet);
    }
    memset(flag_buf, 0, sizeof(flag_buf));

    int selected = -1;
    char        *line     = NULL;
    size_t       cap      = 0;
    ssize_t      len;

    puts("Svenska Trasselnät HAN/P1 verktyg <NOT FOR PROD>");
    puts("-----------------");
    print_help();
    putchar('\n');

    for (;;) {
        printf("> ");
        fflush(stdout);

        len = getline(&line, &cap, stdin);
        if (len < 0)
            break;

        /* Strip trailing newline. */
        if (len > 0 && line[len - 1] == '\n')
            line[--len] = '\0';

        /* Split into verb and optional remainder. */
        char *verb = line;
        char *arg  = NULL;
        char *sp   = strchr(line, ' ');
        if (sp) {
            *sp = '\0';
            arg  = sp + 1;
        }

        if (!*verb)
            continue;

        if (strcmp(verb, "list") == 0) {
            cmd_list();
        } else if (strcmp(verb, "select") == 0) {
            cmd_select(&selected, arg);
        } else if (strcmp(verb, "read") == 0) {
            cmd_read(procs, selected);
        } else if (strcmp(verb, "send") == 0) {
            cmd_send(procs, selected, arg);
        } else if (strcmp(verb, "help") == 0) {
            print_help();
        } else if (strcmp(verb, "quit") == 0 || strcmp(verb, "exit") == 0) {
            break;
        } else {
            printf("Unknown command '%s'. Type 'help' for usage.\n", verb);
        }
    }

    free(line);
    ports_shutdown(procs);
    return 0;
}
