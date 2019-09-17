;An assembly program jumping to an address located in an uniitialized part of memory.
;Can not be solved by constant propagation since the overapproximation approximates the memory content to top

;TODO

SECTION .text
memLoc DB 

SECTION .text

global _start

_start:
        jmp dword [memLoc]

target:
        jmp exit

exit:
        mov ebx, 0;
        mov eax, 1;
        int 0x80;

