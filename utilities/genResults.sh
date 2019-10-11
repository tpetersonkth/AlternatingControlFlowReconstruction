#!/bin/bash

# Note: Currently assumes that the ideal graphs are located in the results directory

# Analyzes a binary using jakstab and a DSE engine
# Params:
#   path to a binary
#   path to directory containing ideal ccfa:s
#   directory to store results
#   port number of DSE
#   timeout in seconds
analyzeBinary () {
    # Rename parameters for readability
    fullpath=$1
    idealDir=$2
    resultDir=$3
    DSEPort=$4
    seconds=$5

    # Extract variables
    path=$(dirname "$fullPath")
    file=$(basename "$fullPath")
    fileNoExt="${file%.*}"
    pathToBin=$(realpath ${path})/$fileNoExt

    # Constant propagation
    analyzeBinarySub $1 $2 $3 $4 $5 "c" "c"

    # Interval analysis
    analyzeBinarySub $1 $2 $3 $4 $5 "i" "i"

    # Constant propagation with DSE
    analyzeBinarySub $1 $2 $3 $4 $5 "c --dse $DSEPort" "cD"

    # Interval analysis with DSE
    analyzeBinarySub $1 $2 $3 $4 $5 "i --dse $DSEPort" "iD"

}

analyzeBinarySub(){
    fullpath=$1
    idealDir=$2
    resultDir=$3
    DSEPort=$4
    seconds=$5
    mode=$6
    identifier=$7

    # Extract variables
    path=$(dirname "$fullPath")
    file=$(basename "$fullPath")
    fileNoExt="${file%.*}"
    pathToBin=$(realpath ${path})/$fileNoExt

    echo "Executing $file in mode $identifier"

    # Constant propagation
    timeout -k 60 $seconds jak -m "$pathToBin" -b -v 1 --cpa $mode
    exitCode=$?

    if [[ "$exitCode" -ne "124" ]]
    then
        mv "$pathToBin"'_ccfa.dot' $(realpath "$resultDir/$fileNoExt"'_'"$identifier"'_ccfa.dot')
        mv "$pathToBin"'_states.dat' $(realpath "$resultDir/$fileNoExt"'_'"$identifier"'_states.dat')
        mv "$pathToBin"'_stats.dat' $(realpath "$resultDir/$fileNoExt"'_'"$identifier"'_stats.dat')
        python3 calculateStats.py $(realpath "$idealDir/$fileNoExt"'_ideal.dot') $(realpath "$resultDir/$fileNoExt"'_'"$identifier"'_ccfa.dot')
    else
        echo "Analysis timed out at $seconds seconds for $file"
    fi

    #Kill jvm in case the analysis resulted in an out of memory error
    pkill -9 java
}

if [ $# -ne 5 ]
then
    echo "Usage: ./genresults.sh [asm dir] [ideal graph dir] [output dir] [port for DSE] [timeout in seconds]"
else
    for fullPath in $1*.asm; do
        if [[ ${fullPath: -8} != "_jak.asm" ]] #Skip jakstab dissasembled assembly
        then
            echo "Attempting to compile $fullPath"
            ../Input/compileStatic.sh $fullPath
            analyzeBinary $fullPath $2 $3 $4 $5
        fi
    done
    for fullPath in $1*.c; do
        fullPath="${fullPath%.*}"
        echo "Attempting to compile $fullPath"
        ../Input/compileMinimal.sh $fullPath #Compiles statically without stdlib
        analyzeBinary $fullPath $2 $3 $4 $5
    done
fi
