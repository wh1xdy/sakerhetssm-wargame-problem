#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

#include "han.h"
#include "handler.h"
#include "port_proc.h"
#include "ports.h"

/* ------------------------------------------------------------------ */

/*
 * Runs in the child process for port index `idx`.
 * stdin/stdout are already connected to the parent's pipes via dup2.
 * Reads line-oriented commands from stdin and responds on stdout.
 */
static void port_loop(int idx)
{
    setvbuf(stdout, NULL, _IONBF, 0);

    char   *line = NULL;
    size_t  cap  = 0;
    ssize_t len;

    while ((len = getline(&line, &cap, stdin)) > 0) {
        /* Strip trailing newline. */
        if (len > 0 && line[len - 1] == '\n')
            line[--len] = '\0';

        if (strcmp(line, "READ") == 0) {
            han_reading_t r;
            han_simulate(ports, port_count, idx, &r);
            han_print_telegram(&ports[idx], &r);
        } else if (strncmp(line, "INIT ", 5) == 0) {
            init_flag_snippet(line + 5);
        } else if (strncmp(line, "SEND ", 5) == 0) {
            ports[idx].handler(&ports[idx], line + 5);
        }
    }

    free(line);
    exit(0);
}

/* ------------------------------------------------------------------ */

port_proc_t *spawn_ports(void)
{
    port_proc_t *procs = malloc(port_count * sizeof(port_proc_t));
    if (!procs) {
        perror("malloc");
        exit(1);
    }

    for (int i = 0; i < port_count; i++) {
        int pfd_in[2], pfd_out[2];

        if (pipe(pfd_in) < 0 || pipe(pfd_out) < 0) {
            perror("pipe");
            exit(1);
        }

        pid_t pid = fork();
        if (pid < 0) {
            perror("fork");
            exit(1);
        }

        if (pid == 0) {
            /* Child: wire up stdin/stdout and close everything else. */
            dup2(pfd_in[0],  STDIN_FILENO);
            dup2(pfd_out[1], STDOUT_FILENO);

            /* Close all fds above stderr so siblings' pipes aren't leaked. */
            for (int fd = 3; fd < 256; fd++)
                close(fd);

            port_loop(i);
            /* port_loop calls exit(), never reaches here */
        }

        /* Parent: close the ends the child uses. */
        close(pfd_in[0]);
        close(pfd_out[1]);

        procs[i].pid       = pid;
        procs[i].to_port   = fdopen(pfd_in[1],  "w");
        procs[i].from_port = fdopen(pfd_out[0], "r");

        if (!procs[i].to_port || !procs[i].from_port) {
            perror("fdopen");
            exit(1);
        }
    }

    return procs;
}

/* ------------------------------------------------------------------ */

void port_read(port_proc_t *proc)
{
    fprintf(proc->to_port, "READ\n");
    fflush(proc->to_port);

    char   *line = NULL;
    size_t  cap  = 0;
    ssize_t len;

    while ((len = getline(&line, &cap, proc->from_port)) > 0) {
        fputs(line, stdout);
        if (strcmp(line, "!\n") == 0)
            break;
    }

    free(line);
}

void port_send(port_proc_t *proc, const char *cmd)
{
    fprintf(proc->to_port, "SEND %s\n", cmd);
    fflush(proc->to_port);

    /* Read handler response lines until the "." sentinel. */
    char   *line = NULL;
    size_t  cap  = 0;
    ssize_t len;

    while ((len = getline(&line, &cap, proc->from_port)) > 0) {
        if (strcmp(line, ".\n") == 0)
            break;
        fputs(line, stdout);
    }

    free(line);
}

void port_init(port_proc_t *proc, const char *snippet)
{
    fprintf(proc->to_port, "INIT %s\n", snippet);
    fflush(proc->to_port);
}

/* ------------------------------------------------------------------ */

void ports_shutdown(port_proc_t *procs)
{
    /* Close all write ends first so every child gets EOF on stdin. */
    for (int i = 0; i < port_count; i++) {
        fclose(procs[i].to_port);
        fclose(procs[i].from_port);
    }
    for (int i = 0; i < port_count; i++) {
        waitpid(procs[i].pid, NULL, 0);
    }
    free(procs);
}
