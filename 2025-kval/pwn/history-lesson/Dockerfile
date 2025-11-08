FROM debian:bookworm-slim AS app

ARG DEBIAN_FRONTEND="noninteractive"
RUN apt-get update && apt-get -y install qemu-system-x86

WORKDIR /app/

COPY src/run.sh ./run
RUN chmod 755 ./run
ARG INITRAMFS="initramfs-server.cpio.gz"
RUN mkdir build
COPY build/${INITRAMFS} ./build/initramfs.cpio.gz
COPY build/bzImage ./build/bzImage

FROM pwn.red/jail
COPY --from=app / /srv

ENV JAIL_PORT=31337 JAIL_TIME=300 JAIL_CONNS=500 JAIL_CONNS_PER_IP=5 JAIL_PIDS=20 JAIL_MEM=300M JAIL_CPU=300 JAIL_POW=1500
