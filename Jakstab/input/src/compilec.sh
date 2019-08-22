#!/bin/bash
file="$1"
if [[ $file == *".c" ]]; then
        file=${file::-2}
fi

gcc -m32 -o $file $1
