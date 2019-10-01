;Example: capabilities of cpa c and DSE

SECTION .text

global _start

_start:
        call function
        jmp exit

function:
        call function2
        mov eax, 2
        ret

function2:
        ret

exit:
        mov ebx, 0;
        mov eax, 1;
        int 0x80;

