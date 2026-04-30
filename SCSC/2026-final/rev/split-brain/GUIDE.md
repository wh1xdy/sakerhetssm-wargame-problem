# Split Brain

| Meta              | Value                          |
| ----------------- | ------------------------------ |
| **Category:**     | Reversing                      |
| **Difficulty:**   | Hard                           |
| **Author:**       | ZetaTwo                        |
| **Technologies:** | Rust, custom VM, multi-process |

## Validation

To validate that the challenge is working correctly, run the "split-brain" and provide "SCSC{1nsan3_iN_th3_Split_brainz}" as input. There is some bug making pipes not play nicely with the binary.

## Challenge Explanation

The challenge follows a standard crackme format. It consists of a compiled binary which takes the flag as input and validates if it is correct. The validation is done by passing flag into a custom VM which runs some code to validate the flag. The custom VM works by forking into a number of subprocesses, each responsible for a separate part of the CPU such as fetcher, decoder, memory, arithmetic, registers, etc. The instructions are decoded into micro ops and passed around in a pipe-based ring buffer. The VM program itself performs some basic arithmetic to validate the flag.

## Intended Solution

By analyzing the binary, the player can understand that it is running a custom VM. By analyzing the architecture, it is then possible to create a simple disassembler and use it on the embedded bytecode to understand what it is doing. This information can then be used to create a script which inverts the checks and calculates the flag.
