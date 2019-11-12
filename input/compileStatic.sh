#!/bin/bash

#Compile to x86 executable:
file="$1"
filename=$(basename "$file")

if [[ $filename == *"."* ]]; then
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
        g++ -m32 --static "$filecpp" -o "$file"
fi

filec="${file}.c"
if test -f "$filec"; then
        echo "Compiling $filec"
        gcc -m32 -O0 --static "$filec" -o "$file"

        #Not yet working(Dead code elimination)
        #gcc -m32 -O0 --entry main -fdata-sections -Wl,--gc-sections "$filec" -o "$file"
        #ld -m elf_i386 -e main --print-gc-sections -o "$file" "$file.o"
fi
