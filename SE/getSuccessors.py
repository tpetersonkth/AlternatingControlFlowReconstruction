"""
Author: Thomas Peterson
Year: 2019
"""
#Built in modules
import sys, logging

#Custom modules
import symbolicExecutor

logger = logging.getLogger(__name__)
logger.setLevel('INFO')

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
