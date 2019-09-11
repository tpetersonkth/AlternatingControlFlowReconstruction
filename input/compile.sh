#!/bin/bash

#Compile to x86 executable:
file="$1"
if [[ $file == *"."* ]]; then
        file=${file::-4}
fi

fileasm="${file}.asm"
if test -f "$fileasm"; then
        echo "Compiling $fileasm"
        nasm -O0 -f elf "$fileasm"
        ld -m elf_i386 -e _start -o "$file" "$file.o"
fi

filecpp="${file}.cpp"
if test -f "$filecpp"; then
        echo "Compiling $filecpp"
        g++ "$filecpp" -m32 -o "$file"
fi

