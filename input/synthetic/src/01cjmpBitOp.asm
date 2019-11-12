;cpa c: Can resolbe all branches without claiming that unreachable is reachable. Eax is propagated correctly to the cmp instruction

SECTION .text

global _start

_start:
        mov eax, 0x7fffffff
        shr eax, 31             ;shift 31 times to the right
        cmp eax, 0
        je exit

unreachable:
        jmp unreachable

exit:
        mov ebx, 0;
        mov eax, 1;
        int 0x80;
