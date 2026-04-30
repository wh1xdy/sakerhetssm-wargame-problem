# Tistel

| Meta            | Value     |
|-----------------|-----------|
| **Category:**   | Reversing |
| **Difficulty:** | Easy      |
| **Author:**     | Dotch     |
| **Tech:**       | C         |

## Validation

Run `make` and then `./validate.sh`.

## Intended Solution

The binary is a verifier-only crackme.

It reads a candidate flag string, pads it to 8-byte blocks (PKCS#7), runs a custom 64-bit Feistel network (32-bit halves, 8 rounds) over each block, then compares the transformed bytes against an embedded target buffer.

Solve by reversing the Feistel round function, subkey derivation, constants, and the final comparison; then invert the Feistel block-by-block to recover the plaintext directly.
