#!/bin/bash

#Checks if a binary finish exeuction under constant propagation and interval analysis

check () {
    # Rename parameters for readability
    fullPath=$1
    cpa=$2
    seconds=$3

    statsFile="$fullPath""_stats.dat"
    if [ -f "$statsFile" ]
    then
        rm $statsFile
    fi

    timeout -k 10 $seconds ../Jakstab/jakstab -m $fullPath -b --cpa $cpa 2>&1 > /dev/null

    if [ -f "$statsFile" ]
    then
        wd=$("pwd")
        cmd="cat $wd"'/'"$statsFile"
        okay=$($cmd | grep 'OK' | wc -l)
        if [ "$okay" -eq "1"  ]
        then 
            echo "cpa $2: yes : $fullPath"
        else
            echo "cpa $2: NO : $fullPath"        
        fi
    else
        echo "cpa $2: NO : $fullPath"
    fi
}

if [ $# -ne 2 ]
then
    echo "Usage: ./checkIfFininshing [folder] [seconds]"
else
    file=$(basename "$1")
    for fullPath in $1*; do
        if [ -f "$fullPath" ]; then
            file=$(basename "$fullPath")
            if [[ $file != *"."* ]]; then
                check $fullPath "c" $2
                check $fullPath "i" $2
            fi
        fi
    done
fi

