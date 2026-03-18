#!/usr/bin/env sh
set -eu

eval "$(opam env)"

if [ "${1:-}" = "canonical" ]; then
  (wc -c < program/canonical.ssa; cat program/canonical.ssa) | dune exec ./main.exe
elif [ "$#" -eq 0 ]; then
  dune exec ./main.exe
else
  echo "Usage: $0 [canonical]" >&2
  exit 1
fi
