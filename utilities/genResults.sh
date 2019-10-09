#!/bin/bash

# Note: Currently assumes that the ideal graphs are located in the results directory

# Analyzes a binary using jakstab and a DSE engine
# Params:
#   path to a binary
#   path to directory containing ideal ccfa:s
#   directory to store results
#   port number of DSE
analyzeBinary () {
    # Rename parameters for readability
    fullpath=$1
    idealDir=$2
    resultDir=$3
    DSEPort=$4

    # Extract variables
    path=$(dirname "$fullPath")
    file=$(basename "$fullPath")
    fileNoExt="${file%.*}"
    pathToBin=$(realpath ${path})/$fileNoExt

    # Constant propagation
    jak -m "$pathToBin" --cpa c
    mv "$pathToBin"'_ccfa.dot' $(realpath "$resultDir/$fileNoExt"'_c_ccfa.dot')
    mv "$pathToBin"'_states.dat' $(realpath "$resultDir/$fileNoExt"'_c_states.dat')
    mv "$pathToBin"'_stats.dat' $(realpath "$resultDir/$fileNoExt"'_c_stats.dat')
    python3 calculateStats.py $(realpath "$idealDir/$fileNoExt"'_ideal.dot') $(realpath "$resultDir/$fileNoExt"'_c_ccfa.dot')

    # Interval analysis
    jak -m "$pathToBin" --cpa i
    mv "$pathToBin"'_ccfa.dot' $(realpath "$resultDir/$fileNoExt"'_i_ccfa.dot')
    mv "$pathToBin"'_states.dat' $(realpath "$resultDir/$fileNoExt"'_i_states.dat')
    mv "$pathToBin"'_stats.dat' $(realpath "$resultDir/$fileNoExt"'_i_stats.dat')
    python3 calculateStats.py $(realpath "$idealDir/$fileNoExt"'_ideal.dot') $(realpath "$resultDir/$fileNoExt"'_i_ccfa.dot')

    # Constant propagation with DSE
    jak -m "$pathToBin" --cpa c --dse "$DSEPort" 
    mv "$pathToBin"'_ccfa.dot' $(realpath "$resultDir/$fileNoExt"'_cD_ccfa.dot')
    mv "$pathToBin"'_states.dat' $(realpath "$resultDir/$fileNoExt"'_cD_states.dat')
    mv "$pathToBin"'_stats.dat' $(realpath "$resultDir/$fileNoExt"'_cD_stats.dat')
    python3 calculateStats.py $(realpath "$idealDir/$fileNoExt"'_ideal.dot') $(realpath "$resultDir/$fileNoExt"'_cD_ccfa.dot')

    # Interval analysis with DSE
    jak -m "$pathToBin" --cpa i --dse "$DSEPort"
    mv "$pathToBin"'_ccfa.dot' $(realpath "$resultDir/$fileNoExt"'_iD_ccfa.dot')
    mv "$pathToBin"'_states.dat' $(realpath "$resultDir/$fileNoExt"'_iD_states.dat')
    mv "$pathToBin"'_stats.dat' $(realpath "$resultDir/$fileNoExt"'_iD_stats.dat')
    python3 calculateStats.py $(realpath "$idealDir/$fileNoExt"'_ideal.dot') $(realpath "$resultDir/$fileNoExt"'_iD_ccfa.dot')

}

if [ $# -ne 4 ]
then
    echo "Usage: ./genresults.sh [asm dir] [ideal graph dir] [results dir] [port for DSE]"
else
    for fullPath in $1*.asm; do
        if [[ ${fullPath: -8} != "_jak.asm" ]] #Skip jakstab dissasembled assembly
        then

            echo "Attempting to compile $fullPath"
            ../Input/compileStatic.sh $fullPath
            analyzeBinary $fullPath $2 $3 $4
        fi
    done
    for fullPath in $1*.c; do
        fullPath="${fullPath%.*}"
        echo "Attempting to compile $fullPath"
        ../Input/compileMinimal.sh $fullPath #Compiles statically without stdlib
        analyzeBinary $fullPath $2 $3 $4
    done
fi