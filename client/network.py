"""
In this File, the Network connection is defined.

It includes a class to connect to the server and handle the communication to the server.

IMPORTANT: This is the only file that is used to access the network. (Only file with socket objects)
"""
import socket 

class NetworkClientBase:
    def __init__(self, host: str | None = None, port: int | None = None) -> None:

        self.addr = (host, port)
        self.conn: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):

        self.conn.connect(self.addr)

    def recv(self, size: int) -> bytes:

        return self.conn.recv(size)

    def send(self, data: bytes):

        self.conn.send(data)

