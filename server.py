import socket
import select

HEADER_SIZE = 10
IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]

clients = {}


def receive_msg(client_socket):
    try:
        msg_header = client_socket.recv(HEADER_SIZE)

        if not len(msg_header):
            return False

        msg_len = int(msg_header.decode("utf-8").strip())
        return {"header": msg_header, "data": client_socket.recv(msg_len)}

    except:
        return False


while True:
    read_sockets, _, execption_sockets = select.select(
        sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_msg(client_socket)
            if not user:
                continue
            else:
                sockets_list.append(client_socket)
                clients[client_socket] = user
                username = user['data'].decode("utf-8")
                print(
                    f"Accepted new connection from {client_address[0]}:{client_address[1]} with username {username}")

        else:
            msg = receive_msg(notified_socket)

            if not msg:
                client_name = clients[notified_socket]['data'].decode("utf-8")
                print(f"Connection closed from {client_name}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]
            user_name = user['data'].decode("utf-8")
            msg_data = msg["data"].decode("utf-8")
            print(f"Received message from {user_name} : {msg_data}")

            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(
                        user['header'] + user['data'] + msg['header'] + msg['data'])
    for notified_socket in execption_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
