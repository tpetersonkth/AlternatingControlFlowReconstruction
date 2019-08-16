#!/bin/bash

#Compile to x86 executable:
file="$1"
if [[ $file == *"."* ]]; then
        file=${file::-4}
fi
echo "Compiling $file.asm"
nasm -f elf "$file.asm"
ld -m elf_i386 -e _start -o "$file" "$file.o"
