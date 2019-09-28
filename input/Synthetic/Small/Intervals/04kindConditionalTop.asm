;cpa c: can not resolve jmp eax
;cpa i: can not resolve jmp eax. It should be noted that it does not determine that "eax = [0,10mb]1mb" after "and eax, 0x00A00000"
;DSE: Determines a successor of jmp eax to be 0x0 but that this path is infeasible
;Example: Can be used as an example for when stried interval analysis would be useful in theory.

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

        mov eax, dword [buf]  ; x = T (Assume eax is x)
        and eax, 0x00A00000     ; x = [0,10mb]1mb (However, only happens in theory..)
jump:
        jmp eax

