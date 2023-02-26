"""
In this File, the Network connection is defined.

It includes a class to connect to the server and handle the communication to the server.

IMPORTANT: This is the only file that is used to access the network. (Only file with socket objects)
"""
import socket 

class NetworkClientBase:
    def __init__(self, host: str | None = None, port: int | None = None) -> None:
    # Host (Name oder IP des Servers) und Port (Nummer, auf dem der Server lauscht)
    # werden als Argumente akzeptiert
        self.addr = (host, port)
        self.conn: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Instanzvariablen werden initialisiert

    def connect(self, username: str, password: str, lobby: str) -> bool:
    # Zeigt, ob verbunden wurde oder nicht
        self.conn.connect(self.addr)
        # Verbindung mit Server mit den Adressdaten von "self.addr" aufgebaut
        data = f"{username}-{password}-{lobby}"
        self.send(data.encode())
        # Nachricht wird erstellt und an Server geschickt + Umwandlung in Bytes
        approved = self.recv(1024).decode()
        # Antwort vom Server wird erwartet + Umwandlung in einen String
        if approved == "connected":
            return True
        else:
            return False
        # Es wird geschaut, ob der Server die Verbindung akzeptiert hat oder nicht

    def recv(self, size: int) -> bytes:
    # Nachricht mit bestimmter Größe wird empfangen und zurückgegeben
        return self.conn.recv(size)

    def send(self, data: bytes):
    # Byte Objekt wird an Server geschickt
        self.conn.send(data)




