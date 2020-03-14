import socket
import select
import errno
import sys

HEADER_SIZE = 10
IP = "127.0.0.1"
PORT = 1234

my_username = input("Username : ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username = my_username.encode("utf-8")
username_header = f"{len(username):<{HEADER_SIZE}}".encode("utf-8")
client_socket.send(username_header + username)

while True:
    msg = input(f"{my_username} >: ")

    if msg:
        msg = msg.encode("utf-8")
        msg_header = f"{len(msg):<{HEADER_SIZE}}".encode("utf-8")
        client_socket.send(msg_header + msg)
    try:
        while True:
            username_header = client_socket.recv(HEADER_SIZE)
            if not len(username_header):
                print("Connection closed by the server")
                sys.exit()
            username_len = int(username_header.decode("utf-8").strip())
            username = client_socket.recv(username_len).decode("utf-8")

            msg_header = client_socket.recv(HEADER_SIZE)
            msg_len = int(msg_header.decode("utf-8").strip())
            msg = client_socket.recv(msg_len).decode("utf-8")

            print(f"{my_username} >: {msg}")
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading Error',str(e))
            sys.exit()
        continue

    except Exception as e:
        print('General Error',str(e))
        sys.exit()
