%include 'functions.asm'

SECTION .text
global _start

_start:
        pop ecx

nextArg:
        cmp ecx, 0
        jz noMoreArgs
        pop eax
        call sprintLF
        dec ecx
        jmp nextArg

noMoreArgs:
        call quit
