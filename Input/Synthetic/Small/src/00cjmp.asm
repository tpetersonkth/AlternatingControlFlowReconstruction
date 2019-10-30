;cpa c: Can propagate eax=0 to the cmp instruction and resolves all branches without claiming that unreachable can be reached
;Note: Strange extra instruction in cfa graph?
;Example: Good example of constant propagation basics
SECTION .text

global _start

_start:
        mov eax, 0
        add eax, 20
        mov edi, 12
        sub eax, 30
        add edi, 10
        add eax, 10
        cmp eax, 0
        je exit

unreachable:
        jmp unreachable

exit:
        mov ebx, 0
        mov eax, 1
        int 0x80
