# Setting up chroot below
FROM ubuntu@sha256:186072bba1b2f436cbb91ef2567abca677337cfc786c86e107d25b7072feef0c AS chroot

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/

COPY Makefile /home/ctf/
COPY main.c /home/ctf/
COPY flag.txt /home/ctf/flag.txt
RUN apt-get update
RUN apt-get install -y make gcc
WORKDIR /home/ctf
RUN make

# Now setting up the actual container
FROM ghcr.io/google/nsjail/nsjail:latest

COPY --from=chroot / /chroot

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y netcat-traditional openssl libssl3 libssl-dev

ENTRYPOINT nsjail --port 1337 --chroot /chroot/ --user 1337 --group 1337 --cwd /home/ctf/ --tmpfsmount /tmp --bindmount_ro /dev/urandom:/dev/urandom --bindmount_ro /etc/resolv.conf:/etc/resolv.conf /home/ctf/keyvault

HEALTHCHECK --start-period=20s --start-interval=1s CMD nc -zv 127.0.0.1 1337 || exit 1