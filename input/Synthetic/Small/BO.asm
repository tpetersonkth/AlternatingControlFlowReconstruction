;int.asm
;This file contains a syscall to write. It is used to test how jakstab and manticore
;handles the int instruciton
;
;Results: It appears that jakstab can handle syscalls by skipping them. This is an okay
;approach in a lot of cases. However, when the last instruction is a sys_exit, jakstab keeps executing the following bytes

SECTION .data
msg     db      'Password',0x0A

SECTION .text

global _start

_start:
        jmp printPwd


printPwd:
        mov edx, 9;
        mov ecx, msg;
        mov ebx, 1;
        mov eax, 4;
        int 0x80;
        mov eax, 0;

exit:
        mov ebx, 0;
        mov eax, 1;
        int 0x80;

