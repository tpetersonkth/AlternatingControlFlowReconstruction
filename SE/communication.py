"""
Author: Thomas Peterson
Year: 2019
"""

#TODO smaller recv buffer and concatentation of messages

import socket

HOST = 'localhost'  # Standard loopback interface address (localhost)
PORT = 65430        # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1048576) #1 mb buffer
            if not data:
                break
            print("Recieved: " + str(data))
            conn.sendall(b'All good, I\'ll analyze the paths!'+b'\n')


def isValidRequest():
    pass
