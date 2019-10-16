#!/bin/bash

if [ $# -ne 2 ]
then
    echo "Usage: ./genereateCFAs [directory with binaries] [output directory]"
else
    file=$(basename "$1")
    for fullPath in $1*; do

        # Check that it is a file rather than a directory
        if [ -f "$fullPath" ]; then
            file=$(basename "$fullPath")
            if [[ $file != *"."* ]]; then
                # TODO: Add timeout?
                echo "Generating CFA for: $fullPath"
                pythonScript=$(realpath $(pwd)'/generateCFA.py')
                python3 generateCFG.py $fullPath $2
            fi
        fi
    done
fi

