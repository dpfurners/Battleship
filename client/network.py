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
        # Instanzvariablen werden initialisiert

    def connect(self, username: str, password: str, lobby: str) -> bool:
        self.conn.connect(self.addr)
        # Verbindung zur Adresse wird hergestellt
        data = f"{username}-{password}-{lobby}"
        # Datenstrom
        self.send(data.encode())
        # An Server gesendet
        approved = self.recv(1024).decode()
        # Empfangen vom Server
        if approved == "connected":
            return True
        else:
            return False
        # Schaut, ob Verbindung besteht
    def recv(self, size: int) -> bytes:
    # Erhalten von Daten als Bytes
        return self.conn.recv(size)

    def send(self, data: bytes):
    # Sendet von Daten als Bytes
        self.conn.send(data)


