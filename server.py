import socket
import time
import random
import pickle


HEADER_SIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1234))
s.listen(5)

while True:
    clientsocket, address = s.accept()
    print(f"Conentiion from {address} has been established!")

    data = {1: "Hello,", 2: " World!"}
    msg = pickle.dumps(data)
    msg = bytes(f"{len(msg):<{HEADER_SIZE}}", "utf-8") + msg

    clientsocket.send(msg)
