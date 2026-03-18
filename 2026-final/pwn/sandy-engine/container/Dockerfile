FROM debian:bookworm-slim@sha256:a1363ada3b45cb3ebc74c78943558f8b0c2b59aaa194d8224e1b02cfd5d78583 AS chroot
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends python3 && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/

COPY d8 /home/ctf/d8
COPY snapshot_blob.bin /home/ctf/snapshot_blob.bin
COPY run.py /home/ctf/run.py
COPY flag.txt /home/ctf/flag.txt

RUN chmod +x /home/ctf/d8 /home/ctf/run.py

FROM ghcr.io/google/nsjail/nsjail:latest

COPY --from=chroot / /chroot

ENTRYPOINT nsjail --port 1337 --chroot /chroot/ --user 1337 --group 1337 --cwd /home/ctf/ --tmpfsmount /tmp --bindmount_ro /etc/resolv.conf:/etc/resolv.conf --rlimit_as inf /usr/bin/python3 /home/ctf/run.py
