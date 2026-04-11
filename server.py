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

    # Announce to everyone else that the new user has joined
    other_names = []
    for key in clients:
        if key != username:
            message = f"{username} has joined the chat!\n"
            clients[key].send(message.encode())
            other_names.append(key)

    # Welcome new client
    message = f"Welcome {username}!\n"
    if len(other_names) > 0:
        if len(other_names) == 1:
            message += f"{other_names[0]} is also here!\n"
        else:
            message += f"{', '.join(other_names[:-1])} and {other_names[-1]} are also here!\n"
    else:
        message += f"You are the only one here!\n"
    clients[username].send(message.encode())

    # Log new user
    print(f"{username} has joined the chat!")

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

                            # Log DM
                            print(f"[DM from {username} to {clients[key]}] {" ".join(message.split()[1:])}")
                if is_dm:
                    continue

                # Handle group message
                for key in clients:
                    if key != username:
                        clients[key].send(f"[{username}] {message}\n".encode())

                # Log group message
                print(f"[{username}] {message}")

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

    # Log user quit
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