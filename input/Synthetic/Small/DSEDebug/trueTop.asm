;Jump to the value of the system time. This should be an unresolvable top.
;Can be resolved with cpa c and DSE (DSE can call the syscall to get the time and deduce the target of the jmp eax instruction..)

SECTION .bss
buf      resb 1

SECTION .text

global _start

_start:
        mov eax, 0x0d
        mov ebx, buf
        int 0x80
        movzx eax, word [buf]
        jmp eax

