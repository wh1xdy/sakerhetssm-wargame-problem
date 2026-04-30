#!/bin/sh
tar -czf dist.tar.gz \
    container/Dockerfile \
    container/ld-2.40.so \
    container/libc.so.6 \
    container/libgcc_s.so.1 \
    container/libm.so.6 \
    container/libstdc++.so.6 \
    container/main \
    container/main.cpp

