;An assembly program jumping to an address stored at a memory location. Can be solved since
;constant propagation can propagate constants to memory.

SECTION .data
memLoc DD 0

SECTION .text

global _start

_start:
        mov dword [memLoc], target
        jmp dword [memLoc]

target:
        jmp exit

exit:
        mov ebx, 0;
        mov eax, 1;
        int 0x80;

