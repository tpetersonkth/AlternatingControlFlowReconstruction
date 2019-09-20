;An assembly program containing two call instructions and one ret instruciton
;Jakstab can only find the path through the first call instruction and thus ret is determined to only
;have the successor to the second call instruction. Thus, jakstab can not identify that control flows
;to jmp exit

SECTION .text

global _start

_start:
        call function
        call function
        jmp exit

function:
        ret

exit:
        mov ebx, 0;
        mov eax, 1;
        int 0x80;

