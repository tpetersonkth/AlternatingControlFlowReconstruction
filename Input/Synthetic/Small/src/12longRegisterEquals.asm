;This file contains an instruction that sets 2 registers to the same value and
;a branch-statement that checks if the two registers are equal.
;
;cpa c/i/b/x: Claims that exc1 and unreachable are reachable. Thus, identifying 4 paths.
;DSE: can identify that there is only one possible path

SECTION .text

global _start

_start:
        mov eax, ebx
        cmp eax, ebx
        jne ecx1

ecx0:
        mov ecx, 0
        jmp check

ecx1:               ;ecx1 is unreachable
        mov ecx, 1
        jmp check

check:
        add ecx, ecx
        cmp ecx, 0
        je exit

unreachable:
        jmp edx     ;Top

exit:
        mov ebx, 0
        mov eax, 1
        int 0x80


