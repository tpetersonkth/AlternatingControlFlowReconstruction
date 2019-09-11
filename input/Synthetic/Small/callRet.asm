;An assembly program containing a call and ret instruciton
;cpa c: Can not resolve the target of the ret instruction since it uses memory content
;cpa cs: All branches can be resolved.

SECTION .text

global _start

_start:
        call function
        jmp exit

function:
        ret

exit:
        mov ebx, 0;
        mov eax, 1;
        int 0x80;

