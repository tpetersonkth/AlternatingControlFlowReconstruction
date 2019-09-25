;cpa c: can not resolve jmp eax
;cpa i: can not resolve jmp eax
;DSE: suggests that jmp eax can jump to 0x0 but the path ending in 0x0 is infeasible since 0x0 does not contain a valid instruction(Most probably)

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

        movzx eax, word [buf]   ; x = T (Assume eax is x)
        and eax, 0x00A00000     ; x = [0,10mb]1mb
        cmp eax, 0
        je jump
        add eax, 1
jump:
        jmp eax                 ; x = [0,10mb]1mb U [0+1,10mb+1]1mb

