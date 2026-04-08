import socket
import threading

clients: dict[str, socket.socket] = {}

# Bind to port 5000
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(('', 5000))
server_sock.listen()

def handle_client(sock):
    # Receive username from client and store in clients dict
    username = sock.recv(1024).decode()
    clients[username] = sock

    # Announce to everyone that the new user has joined
    for key in clients:
        if key != username:
            message = f"{username} has joined the chat!\n"
            clients[key].send(message.encode())
        else:
            message = f"Welcome {username}!\n"
            clients[key].send(message.encode())

    # Continuously pass messages to other clients
    while True:
        # Receive data from client
        message = sock.recv(1024).decode()

        # Handle quit
        if message == "quit":

            # Quit message
            for key in clients:
                if key != username:
                    message = f"{username} has left the chat!\n"
                    clients[key].send(message.encode())

            # Escape loop to end thread
            break

        # Pass along message
        else:
            for key in clients:
                clients[key].send(f"{username}: {message}\n".encode())

    # Close socket
    clients[username].close()

    # Remove client from dict
    del clients[username]

while True:
    try:
        sock, addr = server_sock.accept()
        t = threading.Thread(target=handle_client, args=(sock,))
        t.start()

    except KeyboardInterrupt:
        break

# Close everything
for key in clients:
    clients[key].close()
server_sock.close()