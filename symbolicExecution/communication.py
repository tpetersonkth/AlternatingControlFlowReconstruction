"""
Author: Thomas Peterson
Year: 2019
Description: A file to handle the socket communication
"""

import socket, logging, globalLogger
from globalLogger import logger

#Raised when the client closes a socket
class socketClosedException(Exception):
   pass

class Communication():
    conn = None
    encoding = "utf-8"
    socket = None

    #Initializes a clase instance with a port
    def __init__(self,port):
        self.host = 'localhost' # Standard loopback interface address (localhost)
        self.port = port        # Port to listen on

        #Set up socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen()

    #Waits for a connection
    def connect(self):
        self.conn, addr = self.socket.accept()

    #Waits for data from the client
    def getWork(self):
        BUFFERSIZE = 1024 # 1kb buffer

        data=b''
        while True:
            rec = self.conn.recv(BUFFERSIZE)
            if(not rec):
                self.conn = None
                raise socketClosedException
            data+=rec
            if self.isValidRequest(data):
                break
            else:
                pass

        return self.formatRequest(data).decode(self.encoding)

    #Send an answer back to the client
    def sendAnswer(self,answer):
        answer = str.encode(answer,self.encoding)
        self.conn.sendall(answer + b'\n')

    #Close the connection
    def close(self):
        self.conn.close()
        self.conn = None

    #Check that a message is a valied request
    def isValidRequest(self, message):
        if message.startswith(b'START') and message.endswith(b'END'):
            return True
        return False

    #Format the request to not include the START and END tags
    def formatRequest(self, request):
        if not self.isValidRequest(request):
            raise Exception

        #Remove START and END
        return request[5:-3]
