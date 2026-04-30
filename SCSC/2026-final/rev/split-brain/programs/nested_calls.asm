; nested_calls.asm
; Demonstrates a 2-level deep function call, requiring saving
; the link register (lr/r14) on the stack.

main:
    LUI sp, 0x10
    LDI sp, 0x00

    CALL outer_func

    ; Print a newline after everything is done.
    LDI r0, 0x0A
    SYS PUTC

    SYS HALT

; This function calls another function, so it must
; save and restore the link register.
outer_func:
    LDI r0, 0x4F  ; 'O'
    SYS PUTC
    LDI r0, 0x28  ; '('
    SYS PUTC

    PUSH lr       ; Save return address to main
    CALL inner_func
    POP lr        ; Restore return address to main

    LDI r0, 0x29  ; ')'
    SYS PUTC
    LDI r0, 0x6F  ; 'o'
    SYS PUTC
    RET

; This is the deepest function, it can just return.
inner_func:
    LDI r0, 0x49  ; 'I'
    SYS PUTC
    RET
