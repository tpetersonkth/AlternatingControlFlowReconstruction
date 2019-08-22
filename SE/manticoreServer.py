"""
Author: Thomas Peterson
Year: 2019
"""

#Built in modules
import sys, logging

#Custom modules
import symbolicExecutor, pathsObject, pathObject, communication

logger = logging.getLogger(__name__)


def main():
    if (len(sys.argv) < 2):
        print("Usage: Python manticoreServer.py [port number]")
        sys.exit(0)
    port=sys.argv[1]
    print("[*] Starting server..")
    server = Server(int(port))
    server.run()

class Server():
    connection = None

    def __init__(self, port):
        self.connection = communication.Communication(port)

    def run(self):
        # Work loop
        while True:
            print("[*] Waiting for connection..")
            self.connection.connect()
            print("[*] Connection received!")
            request = self.connection.getWork()
            request = request.split("\n")
            program = request[0]
            paths = formatPaths(request[1:])

            print(request)
            print("Program: "+program)
            print("Number of paths received: " + str(paths.pathsLen))

            symbolicExecutor.executeDirected(program, paths)

            self.connection.sendAnswer("Everything okay")


#Deprecated
def loadPathsFromFile(filename):

    with open(filename, "r") as f:
        lines = f.readlines()

    return formatPaths(lines)

def formatPaths(lines):
    paths = []
    for line in lines:
        if line == '':
            continue
        path = line.split(",")
        path = [int(i.strip(), 16) for i in path]  # Remove newline characters and convert to integers
        paths.append(pathObject.PathObject(path))
    return pathsObject.PathsObject(paths)

if __name__ == "__main__":
    main()
