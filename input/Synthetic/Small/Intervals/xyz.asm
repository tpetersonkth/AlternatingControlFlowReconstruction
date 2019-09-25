;Jumps to _start + user input

SECTION .bss
buf      resb 1

SECTION .text

global _start

_start:
        mov  edx, 1             ; max length
        mov  ecx, buf           ; pointer to buffer
        mov  ebx, 0             ; stdin
        mov  eax, 3             ; sys_read
        int  80h                ; perform syscall

        movzx eax, word [buf]   ; eax is now top. x = T
        mov ebx, eax            ; y = x
        sub eax, ebx            ; z = x-y
        jmp eax

