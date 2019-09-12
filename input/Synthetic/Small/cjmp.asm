;cpa c: Can propagates eax=0 to the cmp instruction and resolves all branches without claiming that unreachable can be reached

;Note: Strange extra instruction in cfa graph?

SECTION .text

global _start

_start:
        mov eax, 0
        cmp eax, 0
        je exit

unreachable:
        jmp unreachable

exit:
        mov ebx, 0
        mov eax, 1
        int 0x80
