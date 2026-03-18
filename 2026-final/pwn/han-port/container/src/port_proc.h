#pragma once

#include <sys/types.h>
#include <stdio.h>

typedef struct {
    pid_t  pid;
    FILE  *to_port;    /* parent writes commands  */
    FILE  *from_port;  /* parent reads responses  */
} port_proc_t;

port_proc_t *spawn_ports(void);
void port_init(port_proc_t *proc, const char *snippet);
void port_read(port_proc_t *proc);
void port_send(port_proc_t *proc, const char *cmd);
void ports_shutdown(port_proc_t *procs);
