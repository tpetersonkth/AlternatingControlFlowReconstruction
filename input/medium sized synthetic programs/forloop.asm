SECTION .text
global  _start

_start:
        mov     eax, 0
forLoop:
        cmp     eax, 5
        je      end
        inc     eax
        jmp     forLoop
end:
        mov     ebx, 0
        mov     eax, 1
        int     0x80
