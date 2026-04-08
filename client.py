import tkinter as tk
from ctypes.wintypes import tagMSG
from tkinter import scrolledtext, simpledialog
import threading
import socket
import queue


class App:
    def __init__(self, window: tk.Tk):
        self.window = window
        self.data_queue = queue.Queue()
        self.running = True

        try:

            # Connect to client
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(('127.0.0.1', 5000))

            # Prompt username
            prompt = "Enter your name:"
            while True:
                self.username = simpledialog.askstring("Username", prompt)

                if self.username is None:
                    self.close()
                    return

                # Handle blank usernames
                if not self.username.strip():
                    prompt = "Name cannot be empty. Enter your name:"
                    continue

                # Handle usernames that are too long
                if len(self.username.strip()) > 15:
                    prompt = "Name cannot be longer than 15 characters. Enter your name:"
                    continue

                # Handle usernames that are more than one word
                if len(self.username.strip().split()) > 1:
                    prompt = "Name cannot be more than one word. Enter your name:"
                    continue

                # Send username to server
                self.sock.send(self.username.strip().encode())
                response = self.sock.recv(1024).decode()

                if response == "__ok__":
                    # Good username, stop prompting
                    self.username = self.username.strip()
                    break
                elif response == "__taken__":
                    # Prompt again if server indicates that the username is taken
                    prompt = "That name is taken, try another:"
                    continue

        # Catch disconnection
        except ConnectionResetError:
            self.close()
            return

        # Show main chat window after username is good
        self.show_window()
        self.build_gui()
        self.update_gui()

        self.socket_thread = threading.Thread(target=self.read_socket)
        self.socket_thread.daemon = True
        self.socket_thread.start()

    def build_gui(self):
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(self.window, height=20, state="disabled")
        self.chat_display.pack(padx=10, pady=10, fill="both", expand=True)

        # Frame to hold message input box and send button on same row
        frame = tk.Frame(self.window)
        frame.pack(padx=10, pady=(0, 10), fill='x')

        # Message input box
        self.input_box = tk.Text(frame, height=3)
        self.input_box.pack(side='left', fill='x', expand=True)

        # Send button
        send_btn = tk.Button(frame, text="Send Message", command=self.send_message)
        send_btn.pack(side='left', padx=(5, 0))

    def send_message(self):
        # Read message (minus the new line at the end)
        message = self.input_box.get("1.0", "end-1c")
        if not message: return

        # Display message
        self.chat_display.config(state='normal')
        self.chat_display.tag_config("green", background="green")
        self.chat_display.insert("end", f"{self.username}: {message}\n", "green")
        self.chat_display.config(state='disabled')

        # Send message to server
        self.sock.send(message.encode())

        # Clear message
        self.input_box.delete("1.0", "end")

    def read_socket(self):
        try:
            while self.running:
                data = self.sock.recv(1024)
                if not data:
                    break
                self.data_queue.put(data.decode())
        
        except Exception as e:
            if self.running:
                self.data_queue.put(f"Error: {e}")


    def update_gui(self):
        try:
            # Read message
            data = self.data_queue.get_nowait()

            # Insert message
            self.chat_display.config(state='normal')
            self.chat_display.insert("end", data)
            self.chat_display.config(state='disabled')

        except queue.Empty:
            pass  # No data yet, ignore
        if self.running:
            self.window.after(100, self.update_gui)  # Check every 100 ms

    def show_window(self):
        self.window.deiconify()

    def close(self):
        self.running = False
        self.sock.close()
        self.window.destroy()


root = tk.Tk()
root.withdraw() # Hide window until username is chosen
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.close)  # Handle window close event
root.mainloop()