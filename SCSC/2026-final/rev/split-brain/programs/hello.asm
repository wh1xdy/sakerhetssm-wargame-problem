; Hello World for Ring-16 v5
; Prints "Hello, World!" followed by a newline.

main:
    LDI r0, 0x48 ; H
    SYS PUTC
    LDI r0, 0x65 ; e
    SYS PUTC
    LDI r0, 0x6C ; l
    SYS PUTC
    SYS PUTC     ; l
    LDI r0, 0x6F ; o
    SYS PUTC
    LDI r0, 0x2C ; ,
    SYS PUTC
    LDI r0, 0x20 ;
    SYS PUTC
    LDI r0, 0x57 ; W
    SYS PUTC
    LDI r0, 0x6F ; o
    SYS PUTC
    LDI r0, 0x72 ; r
    SYS PUTC
    LDI r0, 0x6C ; l
    SYS PUTC
    LDI r0, 0x64 ; d
    SYS PUTC
    LDI r0, 0x0A ; \n
    SYS PUTC

    SYS HALT
