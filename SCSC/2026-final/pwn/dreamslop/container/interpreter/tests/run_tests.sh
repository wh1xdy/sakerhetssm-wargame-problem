#!/usr/bin/env bash
# Runs each example and diffs combined stdout+stderr against its .expected file.
set -u
here="$(cd "$(dirname "$0")/.." && pwd)"
bin="$here/dreamslop"

if [ ! -x "$bin" ]; then
    echo "build the interpreter first: make"
    exit 2
fi

pass=0
fail=0
for src in "$here"/examples/*.db; do
    name="$(basename "$src" .db)"
    expected="$here/examples/$name.expected"
    if [ ! -f "$expected" ]; then
        echo "skip $name (no .expected)"
        continue
    fi
    actual="$("$bin" "$src" 2>&1)" || true
    if [ "$actual" = "$(cat "$expected")" ]; then
        printf 'ok   %s\n' "$name"
        pass=$((pass+1))
    else
        printf 'FAIL %s\n' "$name"
        diff <(printf '%s\n' "$actual") "$expected" | sed 's/^/    /'
        fail=$((fail+1))
    fi
done

echo "----"
echo "$pass passed, $fail failed"
if [ "$fail" -gt 0 ]; then exit 1; fi
