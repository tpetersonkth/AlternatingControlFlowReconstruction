#!/bin/bash
for filename in $1/*.asm; do
        echo "filename: $filename"
        ../Input/compile.sh $filename

        filename=${filename::-4}
        jak -m "$filename" --cpa i
        mv "$filename"'_ccfa.dot' $2
done
