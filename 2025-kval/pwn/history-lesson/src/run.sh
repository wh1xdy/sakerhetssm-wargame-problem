#!/bin/sh

set -e

echo "Welcome to today's history lesson!"
echo "The lesson will commence in 5 seconds"
sleep 5

qemu-system-x86_64 \
     -initrd build/initramfs.cpio.gz \
     -kernel build/bzImage \
     -append "root=/dev/ram console=ttyS0 oops=panic quiet" \
     -nographic \
     -monitor /dev/null \
     -m 256 \
     -smp 1 \
     -no-reboot
