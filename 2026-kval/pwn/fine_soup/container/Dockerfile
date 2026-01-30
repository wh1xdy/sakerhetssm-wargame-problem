FROM debian:bookworm-slim@sha256:d5d3f9c23164ea16f31852f95bd5959aad1c5e854332fe00f7b3a20fcc9f635c AS chroot
ARG DEBIAN_FRONTEND=noninteractive

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/

RUN apt-get update && apt-get install -y --no-install-recommends \
    libc6 libc6-dbg binutils elfutils \
    && rm -rf /var/lib/apt/lists/*

#RUN set -eux; \
#    libc="/lib/x86_64-linux-gnu/libc.so.6"; \
#    buildid="$(readelf -n "$libc" | awk '/Build ID/ {print $3; exit}')"; \
#    b1="$(printf '%s' "$buildid" | cut -c1-2)"; \
#    b2="$(printf '%s' "$buildid" | cut -c3-)"; \
#    dbg="/usr/lib/debug/.build-id/$b1/$b2.debug"; \
#    echo "buildid=$buildid"; \
#    echo "dbg=$dbg"; \
#    test -f "$dbg"; \
#    eu-unstrip -o /home/ctf/libc.so.6.debugfull "$libc" "$dbg"; \
#    readelf -S /home/ctf/libc.so.6.debugfull | grep -q '\.debug_info'

COPY chall /home/ctf/
COPY flag.txt /home/ctf/

# Now setting up the actual container
FROM ghcr.io/google/nsjail/nsjail:latest

COPY --from=chroot / /chroot

ENTRYPOINT nsjail --port 1337 --chroot /chroot/ --user 1337 --group 1337 --cwd /home/ctf/ --tmpfsmount /tmp --bindmount_ro /etc/resolv.conf:/etc/resolv.conf /home/ctf/chall
