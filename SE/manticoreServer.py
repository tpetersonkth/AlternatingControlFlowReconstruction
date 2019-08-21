"""
Author: Thomas Peterson
Year: 2019
"""

#Built in modules
import sys, logging

#Custom modules
import symbolicExecutor, pathsObject,pathObject

logger = logging.getLogger(__name__)

def main():
    if (len(sys.argv) < 3):
        print("Usage: Python manticoreServer.py [path to binary] [path to file containing paths]")
        sys.exit(0)
    program=sys.argv[1]
    filename=sys.argv[2]
    paths = loadPaths(filename)

    symbolicExecutor.executeDirected(program,paths)

def loadPaths(filename):
    paths=[]

    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            path = line.split(",")
            path = [int(i.strip(), 16) for i in path]#Remove newline characters and convert to integers
            paths.append(pathObject.PathObject(path))

    return pathsObject.PathsObject(paths)

if __name__ == "__main__":
    main()