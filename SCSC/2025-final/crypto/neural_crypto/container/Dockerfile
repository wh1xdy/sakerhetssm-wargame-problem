FROM ubuntu:22.04 AS chroot

ARG DEBIAN_FRONTEND=noninteractive

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/

RUN apt update -y && apt upgrade -y
RUN apt install -y sagemath

WORKDIR /home/ctf/
COPY secrets.py .
COPY run_chall.sh .
COPY chall.sage .
RUN chmod 0755 /home/ctf/run_chall.sh && chown -R ctf:ctf /home/ctf/
RUN chmod 1777 /home/ctf
ENV TMPDIR=/tmp

WORKDIR /

FROM ghcr.io/google/nsjail/nsjail:latest



COPY --from=chroot / /chroot
RUN mkdir /chroot/home/ctf/.sage
RUN chown -R 1337:1337 /chroot/home/ctf && chmod 1777 /chroot/home/ctf && chmod 777 /chroot/home/ctf/.sage

ENTRYPOINT nsjail --port 1337 --chroot /chroot/ --rw --user 1337 --group 1337 --cwd /home/ctf/ \
  --tmpfsmount /tmp --bindmount_ro /etc/resolv.conf:/etc/resolv.conf -- ./run_chall.sh
