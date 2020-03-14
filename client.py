import socket

HEADER_SIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))

full_msg = ""
new_msg = True
while True:
    msg = s.recv(HEADER_SIZE)
    if new_msg:
        print(f"New message length : {msg[:HEADER_SIZE]}")
        msg_len = int(msg[:HEADER_SIZE])
        new_msg = False

    full_msg += msg.decode("utf-8")

    if len(full_msg)-HEADER_SIZE == msg_len:
        print("Full message received")
        print(full_msg[HEADER_SIZE:])
        new_msg = True
        full_msg = ""
print(full_msg)
