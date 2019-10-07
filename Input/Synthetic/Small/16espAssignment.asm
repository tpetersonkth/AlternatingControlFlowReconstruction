;CPA c/i: Can resolve all
;Note: Ret instruction is marked as unresolvable in constant propagation even though it is resolved. It is resolved and considered resolved in the interval analysis.
;Exclude?

SECTION .text

global _start

_start:
        mov esp, 0xFFFFFFFF
        sub esp, 4
        mov DWORD[esp],retLocation

retLocation:
        jmp exit

exit:
        mov ebx, 0;
        mov eax, 1;
        int 0x80;

function:
        ret


