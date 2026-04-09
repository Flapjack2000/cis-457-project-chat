import socket
import threading

# Store sockets by unique username
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
            sock.recv(1024)  # wait for client ack before sending welcome
            clients[username] = sock
            break

    for key in clients:
        # Announce to everyone else that the new user has joined
        if key != username:
            message = f"{username} has joined the chat!\n"
            clients[key].send(message.encode())

        # Welcome new client
        else:
            message = f"Welcome {username}!\n"
            clients[key].send(message.encode())

    # Continuously pass messages to other clients
    while True:
        try:
            # Receive data from client
            message = sock.recv(1024).decode()

            # Handle quit
            if message == "quit" or message == "":
                # Escape to quit announcement
                raise ConnectionResetError

            # Pass along message
            else:

                # Handle direct message
                is_dm = False
                first_word = message.split()[0]
                if first_word[0] == "@":
                    for key in clients:
                        if key == first_word[1:]:
                            is_dm = True
                            clients[key].send(f"[DM from {username}] {" ".join(message.split()[1:])}\n".encode())
                            print(f"DM from {username} to {clients[key]}")
                if is_dm:
                    continue

                # Handle group message
                for key in clients:
                    if key != username:
                        clients[key].send(f"[{username}] {message}\n".encode())
                print(f"[{username}] {message}\n")

        # Catch when clients disconnect
        except (ConnectionResetError, ConnectionAbortedError):

            # Quit announcement
            for key in clients:
                if key != username:
                    message = f"[{username}] has left the chat!\n"
                    clients[key].send(message.encode())
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