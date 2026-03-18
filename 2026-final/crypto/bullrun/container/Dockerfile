#FROM debian:bookworm-slim AS chroot

#RUN apt-get update
#RUN apt-get install -y python3 python3-pycryptodome
FROM python:3.12-slim-bookworm AS chroot
RUN pip install pycryptodome

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/

COPY snowden_papers.py /home/ctf/snowden_papers.py
COPY service /home/ctf/service

FROM ghcr.io/google/nsjail/nsjail:latest

COPY --from=chroot / /chroot

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y netcat-traditional

ENTRYPOINT nsjail --port 1337 --chroot /chroot/ --user 1337 --group 1337 --cwd /home/ctf/ --tmpfsmount /tmp --bindmount_ro /etc/resolv.conf:/etc/resolv.conf /usr/local/bin/python3 /home/ctf/service

HEALTHCHECK --start-period=20s --start-interval=1s CMD nc -zv 127.0.0.1 1337 || exit 1
