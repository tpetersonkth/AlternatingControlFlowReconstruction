section .bss
   buf      resb 1                  ; 1000-byte buffer (in data section)

section .text
    global _start

_start:

printloop:
        mov  edx, 1             ; max length
        mov  ecx, buf           ; buffer
        mov  ebx, 0             ; stdin
        mov  eax, 3             ; sys_read
        int  80h                ; perform syscall

        cmp  eax, 0             ; end loop if read <= 0
        jle  end

        mov  edx, eax           ; length
        mov  ecx, buf           ; buffer
        mov  ebx, 1             ; stdout
        mov  eax, 4             ; sys_write
        int  80h                ; Perform syscall

        jmp  printloop          ; go back to read another byte
end:
        mov    eax, 1           ; sys_exit
        mov    ebx, 0
        int    80h

