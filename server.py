import socket
import threading

clients: dict[str, socket.socket] = {}

# Bind to port 5000
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(('', 5000))
server_sock.listen()

def handle_client(sock):
    # Receive username from client and store in clients dict
    username = sock.recv(1024)
    clients[username] = sock

    # Close socket
    clients[username].close()

    # Remove client from dict
    del clients[username]

while True:
    try:
        sock, addr = server_sock.accept()
        t = threading.Thread(target=handle_client, args=(sock,))

    except KeyboardInterrupt:
        break

server_sock.close()