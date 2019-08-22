"""
Author: Thomas Peterson
Year: 2019
"""

import socket

#TODO: Catch sigterm in getWork()

class Communication():
    conn = None
    encoding = "utf-8"
    socket = None

    def __init__(self,port):
        self.host = 'localhost' # Standard loopback interface address (localhost)
        self.port = port        # Port to listen on

        #Set up socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen()

    def connect(self):
        self.conn, addr = self.socket.accept()

    def getWork(self):
        BUFFERSIZE = 1024# 1kb buffer

        data=b''
        while True:
            rec = self.conn.recv(BUFFERSIZE)
            if(rec):
                #print("Recieved.\n " + str(rec))
                data+=rec
                if self.isValidRequest(data):
                    break
        return self.formatRequest(data).decode(self.encoding)

    def sendAnswer(self,answer):
        answer = str.encode(answer,self.encoding)
        self.conn.sendall(answer + b'\n')

    def close(self):
        self.conn.close()
        self.conn = None

    def isValidRequest(self, message):
        if message.startswith(b'START') and message.endswith(b'END'):
            return True
        return False

    def formatRequest(self, request):
        if not self.isValidRequest(request):
            raise Exception

        #Remove START and END
        return request[5:-3]
