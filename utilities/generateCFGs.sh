#!/bin/bash

if [ $# -ne 2 ]
then
    echo "Usage: ./genereateCFGs [directory with binaries] [output directory]"
else
    file=$(basename "$1")
    for fullPath in $1*; do

        # Check that it is a file rather than a directory
        if [ -f "$fullPath" ]; then
            file=$(basename "$fullPath")
            if [[ $file != *"."* ]]; then
                # TODO: Add timeout?
                echo "Analyzing: $fullPath"
                pythonScript=$(realpath $(pwd)'/generateCFG.py')
                python3 generateCFG.py $fullPath $2
            fi
        fi
    done
fi

