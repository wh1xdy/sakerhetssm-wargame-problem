# Character Generator

| Meta              | Value      |
|-------------------|------------|
| **Category:**     | Reversing  |
| **Difficulty:**   | Medium     |
| **Author:**       | ZetaTwo    |
| **Technologies:** | Python     |

## Validation

To validate that the challenge is working correctly, run `validate.sh`.

## Challenge Explanation

The challenge consists of a Python program that takes a character name and generates TTRPG attributes for that character. If the correct character name is provided, the character will be given the flag as a "starting item".
The challenge works by attaching a tracing function with the `sys.settrace` function. This tracing function will then use the line numbers of code executed inside `generate_character` to subtract values from the name (treated as a number).
Add the end of the generation, if the result is 0, the character name is used as a decryption key to decrypt the flag.  

## Intended Solution

The player must read the code and realize this structure, they can then either collect all the line numbers and calculate the the expected value, or tweak the code to start att zero and add the values to finally print the expected value. This value can then be converted back to a string and input as a name to the generator.
