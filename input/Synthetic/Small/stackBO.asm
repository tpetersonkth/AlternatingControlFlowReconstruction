SECTION .data
pass db 'Password', 0x0A

SECTION .text

global _start

_start:
        call function
        jmp exit

function:
        push   ebp
        mov    ebp,esp

        sub esp, 4              ; Allocate buffer of length 4

        mov  edx, 200           ; max length
        mov  ecx, esp           ; buffer
        mov  ebx, 0             ; stdin
        mov  eax, 3             ; sys_read
        int  80h                ; perform syscall

        add esp, 4

        mov    esp, ebp
        pop    ebp
        ret
exit:
        mov ebx, 0
        mov eax, 1
        int 0x80

unreachable:
        mov  edx, 9             ; length
        mov  ecx, pass          ; buffer
        mov  ebx, 1             ; stdout
        mov  eax, 4             ; sys_write
        int  80h                ; perform syscall

