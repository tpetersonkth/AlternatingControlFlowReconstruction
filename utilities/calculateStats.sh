#!/bin/bash

#Calculates accuracy, soundness and precision given a specified directory

if [ $# -ne 2 ]
then
    echo "Usage: ./checkIfFininshing [directory] [Ideal graph dir]"
else
    directory=$1
    idealDir=$2

    file=$(basename "$directory")
    #There is one stat file per binary and mode
    echo "-------------------------------------"
    for fullPath in $1*; do
        if [ -f "$fullPath" ]; then
            base=$(basename "$fullPath")
            if [[ $base != *"_graph_stats.dat" &&  $base == *"_stats.dat" ]]; then
                statsFile=$base
                binary=$(echo $statsFile | cut -d'_' -f 1)
                mode=$(echo $statsFile | cut -d'_' -f 2)
                echo "Calculating stats for $binary in mode $mode"
                python3 calculateStats.py "$idealDir/$binary""_ideal.dot" "$directory/$binary""_$mode""_ccfa.dot" $fullPath
                echo "-------------------------------------"
            fi
        fi
    done
fi

