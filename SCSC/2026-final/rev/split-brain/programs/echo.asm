; echo.asm
; Prompts for input, reads a line, and echoes it back.

main:
    LDI sp, 0x00
    LUI sp, 0x10

    ; Store newline character in R1 for later comparison.
    ; We can't compare against an immediate value, so we need it in a register.
    LDI r1, 0x0A

    ; Print prompt "> "
    LDI r0, 0x3E ; '>'
    SYS PUTC
    LDI r0, 0x20 ; ' '
    SYS PUTC

read_loop:
    SYS GETC      ; Read a character into R0.

    ; Compare the input character with the newline in R1.
    CMP r0, r1
    
    ; If it was a newline (Zero flag is set), jump to the end.
    BRANCH EQ, end_program

    ; It wasn't a newline, so print the character that's in R0.
    SYS PUTC

    ; Loop back to read the next character.
    BRANCH AL, read_loop

end_program:
    ; The last character read was a newline. Print it to finish the line.
    SYS PUTC
    
    ; Halt the machine.
    SYS HALT