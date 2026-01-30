# Stacked

| Meta              | Value        |
|-------------------|--------------|
| **Category:**     | Reversing    |
| **Difficulty:**   | Hard         |
| **Author:**       | ZetaTwo      |
| **Technologies:** | C, custom VM |

## Validation

To validate that the challenge is working correctly, run `validate.sh`.

## Challenge Explanation

The challenge follows a standard crackme format. It consists of a compiled binary which takes the flag as a command-line argument and validates if it is correct. The validation is done by passing flag into a custom stack-based VM. The VM will run a small hardcoded program which validates the input character by character.

## Intended Solution

One solution is to reverse engineer the custom VM and build a small little disassembler for it. This can then be used to disassemble the hardcoded bytecode and analyze the validation logic.
Another approach is to do more dynamic analysis and print out the layout of the VM stack at various points and use this to figure out or brute-force the input one character at a time.
