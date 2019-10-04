#!/bin/bash

#Note: Assumes that the ideal graphs are located in the results directory

echo "$0"
if [ $# -ne 3 ]
then
    echo "Usage: ./genresults.sh [asm dir] [results dir] [port for DSE]"
else
    for fullPath in $1/*.asm; do
        if [[ ${fullPath: -8} != "_jak.asm" ]]
        then
            path=$(dirname "$fullPath")
            file=$(basename "$fullPath")
            fileNoExt="${file%.*}"
            pathToBin=$(realpath ${path})/$fileNoExt

            ../Input/compileStatic.sh $path

            jak -m "$pathToBin" --cpa c

            mv "$pathToBin"'_ccfa.dot' $(realpath "$2/$fileNoExt"'_c_ccfa.dot')
            mv "$pathToBin"'_states.dat' $(realpath "$2/$fileNoExt"'_c_states.dat')
            mv "$pathToBin"'_stats.dat' $(realpath "$2/$fileNoExt"'_c_stats.dat')
            python3 calculateStats.py $(realpath "$2/$fileNoExt"'_ideal.dot') $(realpath "$2/$fileNoExt"'_c_ccfa.dot')

            # jak -m "$path" --cpa i
            # mv "$path"'_i_ccfa.dot' $2
            # mv "$path"'_i_states.dot' $2
            # mv "$path"'_i_stats.dat' $2
            # python3 calculateStats.py "$2/$path"'_ideal.dot' "$2/$path"'_i_ccfa.dot'
        fi
    done
fi

