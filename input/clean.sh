#!/bin/bash

find . -type f -name "*_jak.asm"  -delete
find . -type f -name "*.o" -delete
find . -type f -name "*.dot" -delete
find . -type f  ! -name "*.*"  -delete

#Delete ida files
find . -type f -name "*.i64" -delete
find . -type f -name "*.nam" -delete
find . -type f -name "*.til" -delete
find . -type f -name "*.id*" -delete
