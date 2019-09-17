;An assembly program containing a call and ret instruciton
;cpa c/cs: Can not resolve the target of the jmp eax instruction since eax is loaded from the memory. Because do not know value of stack pointer
;cpa x/b/i: Can resolve all branches

SECTION .text

global _start

_start:
        push retAddr
        jmp function
retAddr:
        jmp exit

function:
        pop eax
        jmp eax

unreachable:
        jmp unreachable

exit:
        mov ebx, 0;
        mov eax, 1;
        int 0x80;

