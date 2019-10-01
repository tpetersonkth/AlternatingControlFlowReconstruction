;An assembly programming misusing the ret instruction
;cpa c: ret instruction could not be resolved as it uses memory but constant prop only propagates registers
;cpa cs: Can not handle, does not report unresolved branches but thinks exe stops at the ret instruction in function.
;it assumes that call and ret instructions are handled in a correct way.

SECTION .text

global _start

function:
        ret

_start:
        mov eax, exit
        push eax
        jmp function
exit:
        mov ebx, 0;
        mov eax, 1;
        int 0x80;

