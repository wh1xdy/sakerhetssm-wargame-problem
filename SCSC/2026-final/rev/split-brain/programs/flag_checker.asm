; flag_checker.asm

; SCSC{1nsan3_iN_th3_Split_brainz}
; Reads 32 bytes of input and checks it against a secret flag.
; The check is: target[i] == (input[i] ^ (i + 0x42))

; --- Memory Layout ---
; 0x1000 - 0x101F : User input buffer
; 0x1020 - 0x103F : Pre-calculated target data buffer


main:
    ; Initialize Stack Pointer to a safe memory region
    LDI sp, 0x00
    LUI sp, 0x20

    ; Initialize the target data in memory
    CALL setup_target_data

prompt:
    ; Print "Flag: "
    LDI r0, 0x46 ; F
    SYS PUTC
    LDI r0, 0x6c ; l
    SYS PUTC
    LDI r0, 0x61 ; a
    SYS PUTC
    LDI r0, 0x67 ; g
    SYS PUTC
    LDI r0, 0x3a ; :
    SYS PUTC
    LDI r0, 0x20 ; " "
    SYS PUTC

    ; Read 32 bytes from the user into the input buffer
    CALL read_user_input

    ; Perform the flag check. R0 will be 1 if correct, 0 if incorrect.
    CALL check_flag

    ; Check the result from the function
    LDI r1, 0x00 
    CMP r0, r1 
    BRANCH EQ, incorrect_path ; If r0 == 0, jump to incorrect

correct_path:
    ; Print "Correct!"
    LDI r0, 0x43 ; C
    SYS PUTC
    LDI r0, 0x6F ; o
    SYS PUTC
    LDI r0, 0x72 ; r
    SYS PUTC
    LDI r0, 0x72 ; r
    SYS PUTC
    LDI r0, 0x65 ; e
    SYS PUTC
    LDI r0, 0x63 ; c
    SYS PUTC
    LDI r0, 0x74 ; t
    SYS PUTC
    LDI r0, 0x21 ; !
    SYS PUTC
    LDI r0, 0x0A ; \n
    SYS PUTC
    BRANCH AL, end_program

incorrect_path:
    ; Print "Incorrect."
    LDI r0, 0x49 ; I
    SYS PUTC
    LDI r0, 0x6E ; n
    SYS PUTC
    LDI r0, 0x63 ; c
    SYS PUTC
    LDI r0, 0x6F ; o
    SYS PUTC
    LDI r0, 0x72 ; r
    SYS PUTC
    LDI r0, 0x72 ; r
    SYS PUTC
    LDI r0, 0x65 ; e
    SYS PUTC
    LDI r0, 0x63 ; c
    SYS PUTC
    LDI r0, 0x74 ; t
    SYS PUTC
    LDI r0, 0x2E ; .
    SYS PUTC
    LDI r0, 0x0A ; \n
    SYS PUTC

end_program:
    SYS HALT

; --- Functions ---

; Reads 32 bytes from stdin and stores them at 0x1000
read_user_input:
    LDI r1, 0x00
    LUI r1, 0x10 ; r1 = pointer to input buffer (0x1000)
    LDI r2, 32   ; r2 = loop counter

read_loop:
    SYS GETC     ; Read char into r0
    STM [r1], r0 ; Store char in buffer
    
    LDI r0, 1    ; r0 = 1
    ADD r1, r0   ; Increment buffer pointer
    SUB r2, r0   ; Decrement counter
    
    CMP r2, r0   ; Check if counter is 1 (we check before it's 0)
    BRANCH NE, read_loop ; If not done, loop

    ; Read the last char
    SYS GETC
    STM [r1], r0
    RET

; The core checking logic
check_flag:
    LDI r1, 0x00
    LUI r1, 0x10 ; r1 = pointer to input buffer (0x1000)
    LDI r2, 0x20
    LUI r2, 0x10 ; r2 = pointer to target buffer (0x1020)
    LDI r3, 0    ; r3 = loop index (i)
    LDI r4, 32   ; r4 = loop limit
    LDI r5, 0x42 ; r5 = XOR constant
    LDI r6, 1    ; r6 = 1 (for increments)
    LDI r10, 1   ; r10 = result status, start with 1 (success)

check_loop:
    LDM r7, [r1] ; r7 = input_char = Mem[r1]
    LDM r8, [r2] ; r8 = target_char = Mem[r2]

    MOV r9, r3   ; r9 = current index (i)
    ADD r9, r5   ; r9 = i + constant
    XOR r7, r9   ; r7 = input_char ^ (i + constant)

    ; This part is the constant-time check.
    ; We subtract the computed value from the target. If they are equal,
    ; the result is 0. We then bitwise-OR this with our status register.
    ; If any check fails (result is non-zero), the status register will become non-zero.
    SUB r8, r7   ; r8 = target - computed. r8 is 0 if they match.
    OR r10, r8   ; If r8 is non-zero, r10 will become non-zero.

    ADD r1, r6   ; input_ptr++
    ADD r2, r6   ; target_ptr++
    ADD r3, r6   ; i++
    CMP r3, r4   ; Have we checked all 32 chars?
    BRANCH NE, check_loop ; If not, loop
    
    ; After the loop, if r10 is still 1, it means all checks passed.
    ; We compare r10 to 1 and set r0 to 1 if equal (success), or 0 otherwise.
    CMP r10, r6  ; Compare status (r10) with 1 (r6)
    BRANCH EQ, check_success ; If Z flag is set (r10==1), it's a success.
    LDI r0, 0    ; Failure case: return 0
    RET
check_success:
    LDI r0, 1    ; Success case: return 1
    RET

; This function is long, but it just initializes the target data in memory.
; It stores the pre-computed values of `flag[i] ^ (i + 0x42)`
setup_target_data:
    LDI r2, 0x20
    LUI r2, 0x10 ; r2 = pointer to target buffer (0x1020)
    LDI r6, 1    ; r6 = 1 (for incrementing pointer)
    LDI r0, 0x11;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x00;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x17;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x06;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x3d;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x76;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x26;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x3a;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x2b;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x25;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x7f;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x12;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x27;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x01;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x0f;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x25;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x3a;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x60;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x0b;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x06;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x26;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x3b;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x31;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x2d;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x05;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x39;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x2e;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x3c;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x37;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x31;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x1a;
    STM [r2], r0;
    ADD r2, r6
    LDI r0, 0x1c;
    STM [r2], r0;
    ADD r2, r6
    RET
