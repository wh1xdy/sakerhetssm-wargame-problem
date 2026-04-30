#!/usr/bin/env bash
docker build -t chall-builder .
docker run --rm -v "$PWD:/out" chall-builder cp /dist/chall.cpython-314-x86_64-linux-gnu.so /out/