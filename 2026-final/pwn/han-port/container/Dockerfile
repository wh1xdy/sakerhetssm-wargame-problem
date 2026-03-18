# Stage 1: Build the binary (gcc not included in final chroot)
FROM debian:trixie-slim@sha256:1d3c811171a08a5adaa4a163fbafd96b61b87aa871bbc7aa15431ac275d3d430 AS builder
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*

COPY src /src

ARG FLAG=SSM{r3act0r_l33k}
RUN gcc -Wall -Wextra -std=c11 -O2 -fno-inline -fno-stack-protector -no-pie -D_FORTIFY_SOURCE=0 -I/src \
        -DFLAG='"'"${FLAG}"'"' \
        -o /han-port \
        /src/main.c \
        /src/han.c \
        /src/ports.c \
        /src/port_proc.c \
        /src/handler.c \
        -lm

# Stage 2: Chroot environment (no build tools)
FROM debian:trixie-slim@sha256:1d3c811171a08a5adaa4a163fbafd96b61b87aa871bbc7aa15431ac275d3d430 AS chroot
ENV DEBIAN_FRONTEND=noninteractive

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf

RUN apt-get update && apt-get install -y --no-install-recommends \
    libc6 libc6-dbg binutils elfutils \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /han-port /home/ctf/han-port
RUN chown root:ctf /home/ctf/han-port && chmod 750 /home/ctf/han-port

# Stage 3: nsjail
FROM ghcr.io/google/nsjail/nsjail:latest@sha256:a58a7293d7ca61cb282afacb5f117cc028aefb6f8cb674e3986b7b38b55ee1db

COPY --from=chroot / /chroot

ENTRYPOINT ["nsjail", "--port", "1337", "--chroot", "/chroot", "--user", "1337", "--group", "1337", "--cwd", "/home/ctf", "--tmpfsmount", "/tmp", "--time_limit", "60", "/home/ctf/han-port"]
