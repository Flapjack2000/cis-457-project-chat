import socket
import threading

clients: dict[str, socket.socket] = {}

# Bind to port 5000
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(('', 5000))
server_sock.listen()

while True:
    try:
        sock, addr = server_sock.accept()

    except KeyboardInterrupt:
        break

server_sock.close()