import socket
import threading

clients: dict[str, socket.socket] = {}

# Bind to port 5000
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(('', 5000))
server_sock.listen()

def handle_client(sock):
    # Receive username from client
    while True:
        username = sock.recv(1024).decode()
        if username in clients:
            sock.send("__taken__".encode())
        else:
            sock.send("__ok__".encode())
            clients[username] = sock
            break

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
        try:
            # Receive data from client
            message = sock.recv(1024).decode()

            # Handle quit
            if message == "quit":

                # Quit announcement
                for key in clients:
                    if key != username:
                        message = f"{username} has left the chat!\n"
                        clients[key].send(message.encode())

                # Escape loop to end thread
                break

            # Pass along message
            else:
                for key in clients:
                    if key != username:
                        clients[key].send(f"{username}: {message}\n".encode())

        # Catch when clients disconnect
        except ConnectionResetError as e:
            print(e)
            break

    # Close socket
    clients[username].close()

    # Remove client from dict
    del clients[username]
    print(username + " has left the chat!")

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