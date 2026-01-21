import socket

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


from config import SERVER_HOST, PORT
from utils import recv_line

class SocketClient:
    def __init__(self):
        self.sock = None

    def connect(self):
        self.sock = socket.socket()
        self.sock.connect((SERVER_HOST, PORT))
        return True

    def send_line(self, msg):
        self.sock.sendall((msg + "|").encode())

    def recv_message(self):
        line = recv_line(self.sock)
        if not line:
            return None, None
        if ":" in line:
            return line.split(":", 1)
        return line, ""

    def close(self):
        try:
            self.sock.close()
        except:
            pass
