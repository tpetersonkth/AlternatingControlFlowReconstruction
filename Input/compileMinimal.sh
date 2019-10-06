#!/bin/bash

#Compile to x86 executable:
file="$1"
filename=$(basename "$file")

if [[ $filename == *"."* ]]; then
        file=${file::-2}
fi


filec="${file}.c"
if test -f "$filec"; then
        echo "Compiling $filec"
        gcc -m32 -O0 --entry main --static -nostdlib "$filec" -o "$file"
fi


