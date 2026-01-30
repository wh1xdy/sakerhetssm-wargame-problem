# Crystal Ball

| Meta              | Value          |
|-------------------|----------------|
| **Category:**     | Reversing      |
| **Difficulty:**   | Medium         |
| **Author:**       | ZetaTwo        |
| **Technologies:** | C++, debugging |

## Validation

To validate that the challenge is working correctly, run `validate.sh`.

## Challenge Explanation

The challenge follows a standard crackme format. It consists of a compiled binary which takes the flag as an input and validates if it is correct. The validation is done by calling a huge tree of functions which modifies an initial buffer to generate a key. This key is used to decrypt the target flag which is then compared against the input. Hidden inside the tree of function calls, there is also a call to `ptrace` which will cause the program to exit if it is being debugged.

## Intended Solution

After some decompilation and analysis, the player should realize that the target flag will sit in memory after the execution of the complex function. If they can debug the program and set a breakpoint at the comparison, they can get the flag. To overcome the debugger detection, they can for example patch out the call to ptrace to allow debugging, or the can change the comparison to a print to instead print the intended flag.
