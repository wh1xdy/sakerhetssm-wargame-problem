# Fragmented

| Meta              | Value                 |
| ----------------- | --------------------- |
| **Category:**     | Reversing             |
| **Difficulty:**   | Hard                  |
| **Author:**       | ZetaTwo               |
| **Technologies:** | Rust, WASM, threading |

## Validation

To validate that the challenge is working correctly, run `validate.sh`.

## Challenge Explanation

The challenge follows a standard crackme format. It consists of a compiled Rust binary which takes the flag as an input and validates if it is correct. The validation is done by taking each bytes and passing it parallel to one of eight different functions implemented as a WebAssembly module. Each such function implements a simple bijective transformation of the flag byte. The transformed bytes are collected and compared against a target value.

## Intended Solution

After some decompilation and analysis, the player should realize what is going on. They need to extract the eight different WASM modules and decompile them to recover the logic. By implementing the reverse logic for each, they can extract the target constant from the binary and use it to compute that flag.
