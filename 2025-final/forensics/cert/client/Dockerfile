FROM ubuntu:22.04 AS chroot

ARG DEBIAN_FRONTEND=noninteractive

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/

COPY cert.pem /home/ctf/
COPY flag.txt /home/ctf/
COPY client /home/ctf/

FROM ghcr.io/google/nsjail/nsjail:latest

COPY --from=chroot / /chroot

ENTRYPOINT nsjail -N --port 1337 --chroot /chroot/ --user 1337 --group 1337 --cwd /home/ctf/ --tmpfsmount /tmp --bindmount_ro /etc/resolv.conf:/etc/resolv.conf -- /home/ctf/client -cacert /home/ctf/cert.pem -flagpath /home/ctf/flag.txt