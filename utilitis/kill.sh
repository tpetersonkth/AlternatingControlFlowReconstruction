#!/bin/bash
echo "Killing $1"
PID=`ps -ef | grep $1 | awk '{ print $2 }'`
kill -9 $PID
