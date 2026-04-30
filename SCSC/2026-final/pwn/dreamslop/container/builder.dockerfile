FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        make \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY interpreter/ ./
CMD make clean && make
