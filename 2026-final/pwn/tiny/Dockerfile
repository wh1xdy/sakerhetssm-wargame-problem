FROM ghcr.io/google/nsjail/nsjail:latest

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y uidmap

RUN groupadd -g 1337 flag && useradd -r -u 1337 -g flag flag
RUN groupadd -g 1338 ctf && useradd -r -u 1338 -g ctf ctf
RUN mkdir -p /home/ctf

WORKDIR /home/ctf
COPY tiny .
COPY flag .
RUN chown flag: ./tiny && \
    chmod 4555 ./tiny && \
    chown flag: ./flag && \
    chmod 400 ./flag

ENTRYPOINT ["nsjail", "--bindmount_ro", "/:/", "--disable_no_new_privs", "--cap", "CAP_SETUID", "--cap", "CAP_SETGID", "--cap", "CAP_SYS_RAWIO", "--disable_clone_newuser", "--port", "1337", "--user", "1338", "--group", "1338", "--cwd", "/home/ctf", "--tmpfsmount", "/tmp", "/bin/bash"]
