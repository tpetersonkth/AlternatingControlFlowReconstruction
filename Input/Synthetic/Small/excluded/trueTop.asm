;Jumps to _start + user input
;Example: A true top for DSE. However, DSE will suggest possible successors.
SECTION .bss
buf      resb 4

SECTION .text

global _start

_start:
        mov  edx, 1             ; max length
        mov  ecx, buf           ; pointer to buffer
        mov  ebx, 0             ; stdin
        mov  eax, 3             ; sys_read
        int  80h                ; perform syscall

        mov eax, dword [buf]
        add eax, _start
        jmp eax

