[bits 64]

ehdr:
  db 0x7F, "ELF"
  db 0x2      ; ELFCLASS64
  db 0x1      ; ELFDATA2LSB
  db 0x1      ; EV_CURRENT
  db 0x0, 0x0 ; ELFOSABI_SYSV, ABI_VERSION
main:
  mov dl, 0x3
  syscall
  ret
  db 0x0, 0x0

  dw 0x2           ; ET_EXEC
  dw 0x3E          ; EM_X86_64
  dd 0x1           ; EV_CURRENT
  dq (main - ehdr) ; e_entry
  dq (phdr - ehdr) ; e_phoff
  dq 0x0           ; e_shoff
  dd 0x0           ; e_flags
  dw (phdr - ehdr) ; e_ehsize
  dw (pgsp - phdr) ; e_phentsize
  dw 0x2           ; e_phnum
  dw 0x40          ; e_shentsize
  dw 0x0           ; e_shnum
  dw 0x0           ; e_shstrndx

phdr:
  dd 0x1           ; PT_LOAD
  dd 0x7           ; PF_X | PF_W | PF_R
  dq 0x0           ; p_offset
  dq 0x0           ; p_vaddr
  dq 0x0           ; p_paddr
  dq (end - ehdr)  ; p_filesz
  dq (end - ehdr)  ; p_memsz
  dq 0x1           ; p_align

pgsp:
  dd 0x6474e551    ; PT_GNU_STACK
  dd 0x7           ; PF_X | PF_W | PF_R
  dq 0x0           ; p_offset
  dq 0x0           ; p_vaddr
  dq 0x0           ; p_paddr
  dq 0x0           ; p_filesz
  dq 0x0           ; p_memsz
  dq 0x10          ; p_align

end:

