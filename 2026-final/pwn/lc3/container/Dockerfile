FROM debian:bookworm-slim@sha256:46ce7bb2760291cd6a422136678e9797a012049a83fddc7efc8206e6ef7544c2 AS chroot
ARG DEBIAN_FRONTEND=noninteractive

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/

COPY chall /home/ctf/
COPY flag.txt /home/ctf/

# Now setting up the actual container
FROM ghcr.io/google/nsjail/nsjail:latest

COPY --from=chroot / /chroot

ENTRYPOINT nsjail --port 1337 --chroot /chroot/ --user 1337 --group 1337 --cwd /home/ctf/ --tmpfsmount /tmp --bindmount_ro /etc/resolv.conf:/etc/resolv.conf /home/ctf/chall
