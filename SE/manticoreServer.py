"""
Author: Thomas Peterson
Year: 2019
"""

#Built in modules
import sys, logging

#Custom modules
import symbolicExecutor, pathsObject, pathObject, communication

logger = logging.getLogger(__name__)
logger.setLevel('INFO')

def main():
    if (len(sys.argv) < 2):
        print("Usage: Python manticoreServer.py [port number]")
        sys.exit(0)
    port=sys.argv[1]
    logger.info("[*] Starting server..")
    server = Server(int(port))
    server.run()

class Server():
    connection = None

    def __init__(self, port):
        self.connection = communication.Communication(port)

    def run(self):
        logger.info("[*] Waiting for connection..")
        self.connection.connect()
        logger.info("[*] Connection received!")
        # Work loop
        while True:
            request = self.connection.getWork()
            request = request.split("\n")
            program = request[0]
            paths = formatPaths(request[1:])

            logger.info(request)
            logger.info("Program: "+program)
            logger.info("Number of paths received: " + str(paths.pathsLen))

            targets = symbolicExecutor.executeDirected(program, paths)

            response = formatResponse(paths,targets)

            print("Sending: " + response)

            self.connection.sendAnswer(response)

def formatResponse(paths,targets):
    response = "START"
    pairs = []
    for pathID in targets.keys():
        pairs.append(hex(paths.lastAddresses[pathID]) + "," + next(iter(targets[pathID]))) #TODO Export all not just first
    response += ":".join(pairs) + "END"
    return response

def formatPaths(lines):
    paths = []
    id = 0
    for line in lines:
        if line == '':
            continue
        path = line.split(",")
        path = [int(i.strip(), 16) for i in path]  # Remove newline characters and convert to integers
        paths.append(pathObject.PathObject(path,id))
        id +=1

    return pathsObject.PathsObject(paths)

#Deprecated
def loadPathsFromFile(filename):

    with open(filename, "r") as f:
        lines = f.readlines()

    return formatPaths(lines)


if __name__ == "__main__":
    main()
