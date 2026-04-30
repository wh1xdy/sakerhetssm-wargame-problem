# Setting up chroot below
FROM debian:bookworm-slim AS chroot

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/

RUN apt-get update && apt-get install -y python3 && rm -rf /var/lib/apt/lists/*

COPY chall.py /home/ctf/
COPY flag.py /home/ctf/
RUN chmod +x /home/ctf/chall.py

# Now setting up the actual container
FROM ghcr.io/google/nsjail/nsjail:latest

COPY --from=chroot / /chroot

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y netcat-traditional

ENTRYPOINT nsjail --port 1337 --chroot /chroot/ --user 1337 --group 1337 --cwd /home/ctf/ --tmpfsmount /tmp --bindmount_ro /etc/resolv.conf:/etc/resolv.conf /home/ctf/chall.py

HEALTHCHECK --start-period=20s --start-interval=1s CMD nc -zv 127.0.0.1 1337 || exit 1
