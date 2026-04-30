# Bark at the Moon

| Meta              | Value       |
|-------------------|-------------|
| **Category:**     | Reversing   |
| **Difficulty:**   | Medium      |
| **Author:**       | ZetaTwo     |
| **Technologies:** | C, Lua, RC4 |

## Validation

To validate that the challenge is working correctly, run `validate.sh`.

## Challenge Explanation

The challenge follows a standard crackme format. It consists of a compiled binary which takes the flag as input and validates if it is correct. The validation is done by passing flag into an embedded Lua interpreter which runs some Lua code to validate the flag.

## Intended Solution

By analyzing the binary, the player can understand that it is using Lua to validate the flag. They can extract the embedded Lua bytecode and disassemble it. They also need to analyze the decryption function to understand that it is RC4. With these components together, they can create a script that inverts all the operations and calculates the flag.
