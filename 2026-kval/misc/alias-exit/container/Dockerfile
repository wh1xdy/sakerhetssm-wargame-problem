FROM debian:bookworm-slim@sha256:d5d3f9c23164ea16f31852f95bd5959aad1c5e854332fe00f7b3a20fcc9f635c AS chroot
ARG DEBIAN_FRONTEND=noninteractive

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    libc6 libc6-dbg binutils elfutils \
    && rm -rf /var/lib/apt/lists/*

COPY bashrc /home/ctf/.bashrc
COPY flag.txt /etc/sup3rs3cr3t/flag.txt

RUN chown -R root:ctf /home/ctf/ && chmod -R 750 /home/ctf/

# Now setting up the actual container
FROM ghcr.io/google/nsjail/nsjail:latest

COPY --from=chroot / /chroot

ENTRYPOINT nsjail --port 1337 --chroot /chroot/ --user 1337 --group 1337 --cwd /home/ctf/ --tmpfsmount /tmp --bindmount_ro /etc/resolv.conf:/etc/resolv.conf -- /bin/bash -i
