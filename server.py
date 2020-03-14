import socket
import time
import random

HEADER_SIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1234))
s.listen(5)

while True:
    clientsocket, address = s.accept()
    print(f"Conentiion from {address} has been established!")

    msg = "Welcome to the server!"
    msg = f"{len(msg):<{HEADER_SIZE}}{msg}"

    clientsocket.send(bytes(msg, "utf-8"))

    while True:
        time.sleep(2)
        msg = str(random.randint(0,999999))
        msg = f"{len(msg):<{HEADER_SIZE}}{msg}"

        clientsocket.send(bytes(msg, "utf-8"))