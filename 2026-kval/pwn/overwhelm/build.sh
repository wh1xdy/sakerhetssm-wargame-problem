#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

FLAG="${1:?No flag provided}"

gcc chall.c -o container/chall -O2 -fno-stack-protector -no-pie -z execstack -std=c99

printf "%s" "$FLAG" > container/flag.txt
chmod 444 container/flag.txt
