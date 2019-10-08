;An assembly program jumping to an address located in an uniitialized part of memory.
;Can not be solved by constant propagation since the overapproximation approximates the memory content to top
;Exclude?

SECTION .text
memLoc DB

SECTION .text

global _start

_start:
        jmp dword [memLoc]

unreachable:
        mov ebx, 0;
        mov eax, 1;
        int 0x80;

