FROM python:3.14.4-slim-bookworm@sha256:336220baf4dc02a9da56db1720ce6d248aa7c62a0445af0ea1876ae76cc99bed
ARG DEBIAN_FRONTEND=noninteractive
 
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir setuptools
 
WORKDIR /build
COPY chall.c setup.py ./
 
RUN python3 setup.py build_ext --inplace \
    && mkdir -p /dist \
    && cp chall.cpython-314-x86_64-linux-gnu.so /dist/
 