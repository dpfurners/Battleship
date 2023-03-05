"""
In this File, the Network connection is defined.

It includes a class to connect to the server and handle the communication to the server.

IMPORTANT: This is the only file that is used to access the network. (Only file with socket objects)
"""
import socket
import pickle


class NetworkClientBase:
    def __init__(self, host: str | None = "localhost", port: int | None = 1234) -> None:

        self.addr = (host, port)
        self.conn: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Instanzvariablen werden initialisiert

    def reset(self):
        self.conn.close()
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Verbindung wird geschlossen und neu erstellt

    def connect(self, username: str, password: str) -> bool | str:
        self.conn.connect(self.addr)
        # Verbindung zur Adresse wird hergestellt
        data = f"{username}-{password}"
        # Datenstrom
        self.send(data)
        # An Server gesendet
        approved = self.recv()
        # Empfangen vom Server
        if approved == "connected":
            return True
        else:
            return approved
        # Schaut, ob Verbindung besteht

    def recv(self) -> any:
        # Erhalten von Daten als Bytes
        return pickle.loads(self.conn.recv(1024*2))

    def send(self, data: any):
        # Sendet von Daten als Bytes
        self.conn.send(pickle.dumps(data))


