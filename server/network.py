"""
In this File, the Network connection is defined.

It includes a class to allow clients to connect to the server,
store the clients as object and handle the communication between the server and the clients.

IMPORTANT: This is the only file that is used to access the network. (Only file with socket objects)
"""
import socket
import database

class NetworkServerBase:
    def __init__(self, host: str, port: int) -> None:

        self.addr = (host, port)
        self.conn: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.bind(host, port)

    def bind(self,  host: str, port: int) -> None:

        self.conn.bind((host, port))

    def accept(self, amount: int = 1) -> None:

        self.conn.listen(amount)
        for _ in range(amount):
            sock, addr = self.conn.accept()
            data = self.recv(1024, sock).decode()
            username, password = data.split("-")
            # todo: Connect to database
            LogIn = database.DB_LogIn(username, password)
            if LogIn[0] == False:
                if LogIn[1] == True:
                    self.send("wrong password".encode(), sock)
                    continue
                else:
                    LogIn = database.DB_SignIn(username, password)
                    if LogIn == False:
                        self.send("something went wrong".encode(), sock)

            self.clients[username] = [sock, addr]
            self.send("connected".encode(), sock)
            print(f"{username}-{password}")

    def recv(self, size: int, client: socket.socket) -> bytes:

        return client.recv(size)

    def send(self, data: bytes, client: socket.socket) -> None:

        client.send(data)


if __name__ == '__main__':
    server = NetworkServerBase("localhost", 1234)
    server.accept()

