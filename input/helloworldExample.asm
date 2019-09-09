SECTION .data
msg     db      'Hello World!', 0x0A

SECTION .text
global _start
_start:
        mov edi,10  ;Set the edi register to 10
dec:
        cmp edi,0   ;Compare edi with 0
        je quit     ;Jump to quit if edi=0
print:
        dec edi     ;Decrement edi by 1
        mov edx, 13 ;Set edx to 13
        mov ecx, msg;Set ecx to the address of msg
        mov ebx, 1  ;Set ebx to 1
        mov eax, 4  ;Set eax to the opcode of write
        int 0x80    ;Perform the syscall
        jmp dec     ;Jump to dec
quit:
        mov ebx, 0  ;Set ebx to 0
        mov eax, 1  ;Set eax to the opcode of exit
        int 0x80    ;Perform the syscall
