;TODO...

SECTION .bss
buf      resb 1

SECTION .text

global _start

_start:
        mov  edx, 1             ; max length
        mov  ecx, buf           ; pointer to buffer
        mov  ebx, 0             ; stdin
        mov  eax, 3             ; sys_read
        int  80h                ; perform syscall

        movzx eax, byte [buf]
        cmp eax, 70
        jle echo

        call function2
        jmp exit
echo:
        call function
        call function2
        jmp exit

function:
        mov  edx, 1             ; length
        mov  ecx, buf           ; buffer
        mov  ebx, 1             ; stdout
        mov  eax, 4             ; sys_write
        int  80h                ; Perform syscall
        ret

function2:
        ret

exit:
        mov ebx, 0;
        mov eax, 1;
        int 0x80;

