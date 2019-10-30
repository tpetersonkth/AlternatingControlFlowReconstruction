;Example: capabilities of cpa c and DSE

SECTION .text

global _start

_start:
        call function1
        jmp exit

function1:
        call function2
        ret

function2:
        ret

exit:
        mov ebx, 0
        mov eax, 1
        int 0x80

