;This file contains an instruction that sets 2 registers to the same value and
;a branch-statement that checks if the two registers are equal.
;
;cpa c/s/i/b/x: Claims that unreachable can be reached from the "je exit" instruction (Assume !ZF).
;Then continues the analysis assuming !ZF
;DSE can determine that unreachable is unreachable

SECTION .text

global _start

_start:
        mov eax,ebx
        cmp eax,ebx
        je exit

unreachable:
        jmp problem

problem:
        jmp eax;

exit:
        mov ebx, 0
        mov eax, 1
        int 0x80


