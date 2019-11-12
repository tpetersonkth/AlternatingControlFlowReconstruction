;TODO: Jump table in x86..

SECTION .bss
buf      resb 1

SECTION .text

global _start

_start:
        push   0x2                      ;b=2
        push   0x1                      ;a=1
        call   calculate
exit:
        mov ebx, 0
        mov eax, 1
        int 0x80

calculate:
        cmp DWORD PTR [ebp+0x8],0x5     ;Compare a with 5
        ja return                       ;if a > 5 go to return b
        mov edx,DWORD PTR [ebp+0x8]     ;move a into edx
        shl edx,0x2                     ;edx = a << 2
 506:   8b 94 02 14 e6 ff ff    mov    edx,DWORD PTR [edx+eax*1-0x19ec]         edx = M(0x50f + edx) //Loads offset from jump table
 50d:   01 d0                   add    eax,edx                                  eax = eax + edx calculates address of relevant case block
 50f:   ff e0                   jmp    eax                                      jump to eax(=511|51d|522|528|52e|524)

00000511 <.L3>:
 511:   8b 45 0c                mov    eax,DWORD PTR [ebp+0xc]                  b = b * b
 514:   0f af 45 0c             imul   eax,DWORD PTR [ebp+0xc]
 518:   89 45 0c                mov    DWORD PTR [ebp+0xc],eax                  move new value of b to memory location of b
 51b:   eb 1e                   jmp    53b <.L9+0x7>

0000051d <.L5>:
 51d:   f7 5d 0c                neg    DWORD PTR [ebp+0xc]                      b = b * -1
 520:   eb 19                   jmp    53b <.L9+0x7>

00000522 <.L6>:
 522:   83 6d 0c 80             sub    DWORD PTR [ebp+0xc],0xffffff80
 526:   eb 13                   jmp    53b <.L9+0x7>

00000528 <.L7>:
 528:   83 6d 0c 01             sub    DWORD PTR [ebp+0xc],0x1                  b = b - 1
 52c:   eb 0d                   jmp    53b <.L9+0x7>

0000052e <.L8>:
 52e:   83 45 0c 01             add    DWORD PTR [ebp+0xc],0x1                  b = b + 1
 532:   eb 07                   jmp    53b <.L9+0x7>

00000534 <.L9>:
 534:   8b 45 08                mov    eax,DWORD PTR [ebp+0x8]                  b = b + a
 537:   01 45 0c                add    DWORD PTR [ebp+0xc],eax
 53a:   90                      nop

return:
 53b:   8b 45 0c                mov    eax,DWORD PTR [ebp+0xc]                  Set eax = b before returning (Pass ret value through reg)
 53e:   5d                      pop    ebp                                      Remove stack frame
 53f:   c3                      ret

Contents of section .rodata:
 05e8 03000000 01000200 35e5ffff 41e5ffff  ........5...A...
 05f8 46e5ffff 4ce5ffff 52e5ffff 58e5ffff  F...L...R...X...

Jump table(Containing negative offsets):
0x565555f0:0xffffe535
0x565555f4:0xffffe541
0x565555f8:0xffffe546
0x565555fc:0xffffe54c
0x56555600:0xffffe552
0x56555604:0xffffe558



