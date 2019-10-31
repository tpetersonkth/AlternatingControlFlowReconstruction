#!/bin/bash

# Analyzes a binary using jakstab and a DSE engine
# Params:
#   path to the binary
#   directory to store results
#   port number of DSE
#   timeout in seconds
#   optional args to jakstab
analyzeBinary () {
    # Rename parameters for readability
    fullpath=$1
    resultDir=$2
    DSEPort=$3
    seconds=$4
    jakstabArgs=$5

    printf "jak args:$jakstabArgs"

    # Extract variables
    path=$(dirname "$fullPath")
    file=$(basename "$fullPath")
    fileNoExt="${file%.*}"
    pathToBin=$(realpath ${path})/$fileNoExt

    # Constant propagation
    analyzeBinarySub $fullpath $resultDir $DSEPort $seconds "c $jakstabArgs" "c"

    # Interval analysis
    analyzeBinarySub $fullpath $resultDir $DSEPort $seconds "i $jakstabArgs" "i"

    # Constant propagation with DSE
    analyzeBinarySub $fullpath $resultDir $DSEPort $seconds "c --dse $DSEPort $jakstabArgs" "cD"

    # Interval analysis with DSE
    analyzeBinarySub $fullpath $resultDir $DSEPort $seconds "i --dse $DSEPort $jakstabArgs" "iD"
}

# Analyzes a binary in a specific mode using jakstab and a DSE engine
# Params:
#   path to the binary
#   directory to store results
#   port number of DSE
#   timeout in seconds
#   mode and optional args to jakstab
#   identifier for filenames(To differentiate between modes)
analyzeBinarySub(){
    fullpath=$1
    resultDir=$2
    DSEPort=$3
    seconds=$4
    mode=$5
    identifier=$6

    printf "path:$1\nresultDir:$2\nDSEPort:$3\nseconds:$4\nmode:$5\nid:$6\n"

    # Extract variables
    path=$(dirname "$fullPath")
    file=$(basename "$fullPath")
    fileNoExt="${file%.*}"
    pathToBin=$(realpath ${path})/$fileNoExt

    echo "Executing $file in mode $identifier"

    # Execute one analysis
    timeout -k 60 $seconds jak -m "$pathToBin" -b -v 1 --cpa $mode
    exitCode=$?

    mv "$pathToBin"'_ccfa.dot' $(realpath "$resultDir/$fileNoExt"'_'"$identifier"'_ccfa.dot')
    mv "$pathToBin"'_states.dat' $(realpath "$resultDir/$fileNoExt"'_'"$identifier"'_states.dat')
    mv "$pathToBin"'_stats.dat' $(realpath "$resultDir/$fileNoExt"'_'"$identifier"'_stats.dat')
    mv "$pathToBin"'_location_count.dat' $(realpath "$resultDir/$fileNoExt"'_'"$identifier"'_location_count.dat')

    if [[ "$exitCode" -eq "124" ]]
    then
        echo "Analysis timed out at $seconds seconds for $file"
    fi

    #Kill jvm in case the analysis resulted in an out of memory error
    pkill -9 java
}


if [ $# -ne 4 && $# -ne 5 ]
then
    echo "Usage: ./genresults.sh [bin dir] [output dir] [port for DSE] [timeout in seconds] [Optional args to jakstab]"
else

    for fullPath in $1*; do
        if [[ ${fullPath: -4} != *"."* ]]
        then
            if test -f "$fullPath"; then #Ensure that it is a file and not a directory
                echo "Analysing $fullPath"
                analyzeBinary $fullPath $2 $3 $4 "${5:-""}"
            fi
        fi
        if [[ ${fullPath: -4} == ".asm" ]]
        then
            if [[ ${fullPath: -8} != "_jak.asm" ]]
            then
                echo "Compiling $fullPath"
                ../Input/compileStatic.sh $fullPath
                analyzeBinary $fullPath $2 $3 $4 "${5:-""}"
            fi
        fi
        if [[ ${fullPath: -2} == ".c" ]]
        then
            fullPath="${fullPath%.*}"
            echo "Compiling $fullPath"
            ../Input/compileMinimal.sh $fullPath #Compiles statically without stdlib
            analyzeBinary $fullPath $2 $3 $4 "${5:-""}"
        fi
    done
fi
