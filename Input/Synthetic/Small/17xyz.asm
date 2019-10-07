;cpa c: can not resolve jmp eax
;cpa i: can not resolve jmp eax
;DSE: Determines the successor of jmp eax to be exit
;Example: Capabilities of DSE to help jakstab


SECTION .bss
buf      resb 1

SECTION .text

global _start

_start:
        mov  edx, 1             ; max length
        mov  ecx, buf           ; pointer to buffer
        mov  ebx, 0             ; stdin
        mov  eax, 3             ; sys_read
        int  0x80                ; perform syscall

        movzx eax, word [buf]   ; x = T
        mov ebx, eax            ; y = x
        sub eax, ebx            ; z = x-y = 0
        add eax, exit
        jmp eax

exit:
        mov ebx, 0
        mov eax, 1
        int 0x80


