"""
Author: Thomas Peterson
Year: 2019
Description: A script which, given a binary and an address, returns a set of possible successors after the given address. 
Note; This file is not used by any other file in the ACFR setup. It is only used for debugging.
"""

#Built in modules
import sys, logging

#Custom modules
import symbolicExecutor

def main():
    if (len(sys.argv) < 3):
        print("Usage: Python getSuccessors.py [path to binary] [address of instruction]")
        sys.exit(0)
    program = sys.argv[1]
    address = int(sys.argv[2],16)
    logger.info("Running with program="+program+" address="+hex(address))
    symbolicExecutor.execute(program,address)

if __name__ == "__main__":
    main()
