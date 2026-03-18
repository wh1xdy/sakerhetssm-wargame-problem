FROM debian:trixie-slim@sha256:1d3c811171a08a5adaa4a163fbafd96b61b87aa871bbc7aa15431ac275d3d430 AS chroot
ENV DEBIAN_FRONTEND=noninteractive

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf

RUN apt-get update && apt-get install -y --no-install-recommends \
    libc6 libc6-dbg binutils elfutils \
    && rm -rf /var/lib/apt/lists/*

COPY chall /home/ctf/
COPY flag.txt /home/ctf/

FROM ghcr.io/google/nsjail/nsjail:latest

COPY --from=chroot / /chroot

RUN chmod +x /chroot/home/ctf/chall

ENTRYPOINT ["nsjail", "--port", "1337", "--chroot", "/chroot", "--user", "1337", "--group", "1337", "--cwd", "/home/ctf", "--tmpfsmount", "/tmp", "--bindmount_ro", "/etc/resolv.conf:/etc/resolv.conf", "/home/ctf/chall"]
