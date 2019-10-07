;CPA c and i: Can not resolve jmp eax.. (Because they assume that eax=Top initially)

SECTION .bss
buf      resb 1

SECTION .text

global _start

increment:
        add eax, 1
        jmp continue

_start:
        and eax,0x1
        cmp eax,0x1
        je increment
continue:
        add eax, exit
        jmp eax

exit:
        nop
        mov ebx, 0
        mov eax, 1
        int 0x80


