import tkinter as tk
from tkinter import scrolledtext
import threading
import socket
import queue


class App:
    def __init__(self, window: tk.Tk):
        self.window = window

        self.data_queue = queue.Queue()
        self.running = True

        self.socket_thread = threading.Thread(target=self.read_socket)
        self.socket_thread.daemon = True  # Allow program to exit even if thread is running
        self.socket_thread.start()

        self.build_gui()
        self.update_gui()

    def build_gui(self):
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(self.window, height=20)
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

        # Send message to server
        self.sock.send(message.encode())

        # Clear message
        self.input_box.delete("1.0", "end")

    def read_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(('127.0.0.1', 5000))
            while self.running:
                data = self.sock.recv(1024)
                if not data:
                    break
                self.data_queue.put(data.decode())
        except Exception as e:
            self.data_queue.put(f"Error: {e}")

    def update_gui(self):
        try:
            data = self.data_queue.get_nowait()
            self.chat_display.insert("end", data)
        except queue.Empty:
            pass  # No data yet, ignore
        if self.running:
            self.window.after(100, self.update_gui)  # Check every 100 ms

    def close(self):
        self.running = False
        self.window.destroy()


root = tk.Tk()
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.close)  # Handle window close event
root.mainloop()
