FROM debian:bookworm-slim

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y build-essential zlib1g-dev

WORKDIR /build
COPY main.c .
CMD ["gcc", "-o", "typo", "main.c", "-lz"]
