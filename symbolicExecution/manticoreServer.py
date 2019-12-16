"""
Author: Thomas Peterson
Year: 2019
Description: A server which leverages manticore to obtain successors of locations given by a client
"""

#Built in modules
import sys, logging, socket, time

#Custom modules
import symbolicExecutor, pathsObject, pathObject, communication
from communication import socketClosedException
from globalLogger import logger

def main():
    if (len(sys.argv) < 2):
        print("Usage: Python manticoreServer.py [port number]")
        sys.exit(0)
    port=sys.argv[1]
    logger.info("Starting server..")
    server = Server(int(port))
    server.run()

#The server class which ret
class Server():
    connection = None

    #Setup a socket on a specified port
    def __init__(self, port):
        self.connection = communication.Communication(port)

    # Serve connections
    def run(self):
        while True:
            logger.info("Waiting for connection..")
            self.connection.connect()
            logger.info("Connection received!")
            # Work loop
            while True:
                try:
                    request = self.connection.getWork()
                except socketClosedException:
                    #Client closed socket
                    logger.info("Client disconnected")
                    break
                except Exception as inst:
                    print("Exception:"+str(inst))
                    break

                milliseconds = round(time.monotonic() * 1000) #Get time in milliseconds
                request = request.split("\n")
                program = request[0]
                paths = formatPaths(request[1:])

                logger.info("Program: "+program)
                logger.info("Number of paths received: " + str(paths.pathsLen))

                args = ["+"*20]*3
                targets = symbolicExecutor.executeDirected(program, paths, args=args)

                response = formatResponse(paths,targets)

                milliseconds = round(time.monotonic() * 1000) - milliseconds
                logger.info("Symbolic execution took: " + str(milliseconds) + " ms")
                logger.debug("Sending: " + response)

                self.connection.sendAnswer(response)

#Formats a response from a set of paths and a dictionary of targets
#The message is expected to be of the format START[pairs]END where [pairs] is a set of control flow edges
def formatResponse(paths,targets):
    response = "START"
    pairs = []
    for pathID in targets.keys():
        for target in targets[pathID]:
            pairs.append(hex(paths.lastAddresses[pathID]) + "," + target) #TODO Export all not just first
    response += ":".join(pairs) + "END"
    return response

#Formats a set of lines into a set of paths
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

if __name__ == "__main__":
    main()
