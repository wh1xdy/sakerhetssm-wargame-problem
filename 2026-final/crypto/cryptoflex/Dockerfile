FROM python:3.13-slim-bookworm AS chroot
RUN pip install pycryptodome

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/

COPY src/server.py /home/ctf/server.py

FROM ghcr.io/google/nsjail/nsjail:latest

ENV FLAG="SSM{s0_fleX1bl3_1t_b3nds_ar0und_4nd_br3aks}"
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y netcat-traditional

COPY --from=chroot / /chroot

ENTRYPOINT [ "nsjail", "--port", "1337", "--chroot", "/chroot/", "--env", "FLAG", "--user", "1337", "--group", "1337", "--cwd", "/home/ctf/", "--tmpfsmount", "/tmp", "--bindmount_ro", "/etc/resolv.conf:/etc/resolv.conf", "/usr/local/bin/python3", "/home/ctf/server.py" ]

HEALTHCHECK --start-period=20s --start-interval=1s CMD nc -zv 127.0.0.1 1337 || exit 1
