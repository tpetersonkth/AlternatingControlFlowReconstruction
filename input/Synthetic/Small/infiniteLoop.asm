;cpa c/cs/b/i/s/x: Claims no unresolved branches and that unreachable is reachable!
SECTION .text

global _start

_start:
        mov eax, 0
loop:
        inc eax
        cmp eax, 10
        jle loopcheck
        mov eax, 1
loopcheck:
        cmp eax, 0
        jne loop
unreachable:
        mov ebx, 0;
        mov eax, 1;
        int 0x80;
