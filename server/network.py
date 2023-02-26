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
    # Host und Port werden als Argumente akzeptiert
        self.addr = (host, port)
        self.conn: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.bind(host, port)
        self.lobby = Lobby()
        # Instanzvariablen werden initialisiert

    def bind(self, host: str, port: int) -> None:
    # Host und Port werden verbunden
        self.conn.bind((host, port))

    def accept(self, amount: int = 1) -> None:
    #
        self.conn.listen(amount)
        # Verbindungen vom Clients werden angenommen
        for _ in range(amount):
            sock, addr = self.conn.accept()
            # Für jedes "amount" wird die Client verbindung angenommen
            data = self.recv(1024, sock).decode()
            # Datenstrom wird empfangen, vom "sock" gelsesn und decodiert
            username, password = data.split("-")
            # Benutzername und Passwort werden durch Trennen des Datenstroms
            # durch "-" extrahiert
            LogIn = database.DB_LogIn(username, password)
            if LogIn[0] == False:
                if LogIn[1] == True:
                    self.send("wrong password".encode(), sock)
                    continue
            # Überprüft, ob das Passwort stimmt
                else:
                    LogIn = database.DB_SignIn(username, password)
                    if LogIn == False:
                        self.send("something went wrong".encode(), sock)
                # Falls alles stimmt, werden Benutzername und Passwort in die
                # Datenbank gespeichert. Wenn ein Fehler auftaucht, wird es
                # dem Client übermittelt
            self.clients[username] = [sock, addr]
            self.send("connected".encode(), sock)
            print(f"{username}-{password}")
            self.lobby.add_player(username)
            # Wenn Benutzername und Passwort übereinstimmen, fügt der Server
            # den Benutzer zur Liste der Clients hinzu, sendet eine Bestätigung
            # an den Client und fügt den Benutzer zur Lobby hinzu.
    def recv(self, size: int, client: socket.socket) -> bytes:

        return client.recv(size)

    def send(self, data: bytes, client: socket.socket) -> None:

        client.send(data)
    #
class Lobby:
# Speichert Informationen über Spieler in der Lobby
    def __init__(self):
        self.players = {}
        # leeres "dict" zum  Speichern
    def add_player(self, username):
        self.players[username] = set()

    def remove_player(self, username):
        del self.players[username]
        for other_player in self.players:
            self.players[other_player].discard(username)

    def add_friend(self, username, friend):
        self.players[username].add(friend)
        self.players[friend].add(username)

    def remove_friend(self, username, friend):
        self.players[username].discard(friend)
        self.players[friend].discard(username)

    def get_friends(self, username):
        return list(self.players[username])


class NetworkServerWithLobby(NetworkServerBase):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)

    def handle_client(self, client: str):
        self.send("Welcome to the lobby!".encode(), self.clients[client][0])
        # Willkommennachricht an Client
        while True:
            friends = self.lobby.get_friends(client)
            if len(friends) == 0:
                self.send("You don't have any friends in the lobby yet.".encode(), self.clients[client][0])
            else:
                friend_str = ", ".join(friends)
                self.send(f"Your friends in the lobby: {friend_str}".encode(), self.clients[client][0])
            # Liste wird überprüft, ob leer oder nicht, falls leer hat der Client keine Freunde in der Lobby,
            # falls nicht leer werden die Namen der Freunde in der Lobby als eine durch
            # Kommas getrennte Zeichenkette formatiert und an den Client gesendet
            self.send("Enter a friend's username to add them, or enter 'start' to begin a game:".encode(), self.clients[client][0])
            # Anforderung zum Starten oder Freund eingeben
            data = self.recv(1024, self.clients[client][0]).decode()
            # Client wartet auf Eingabe
            if data == "start":
                self.send("Starting game...".encode(), self.clients[client][0])
                # TODO code to start game goes here
                break
            elif data in self.clients:
                friend = data
                self.lobby.add_friend(client, friend)
                self.send(f"You are now friends with {friend}!".encode(), self.clients[client])
            # Schaut, ob der Client "start" geschickt hat, falls ja wird das Spiel gestartet und
            # die Schleife beendet, falls der Client einen Benutzernamen (der in der CLient Liste
            # ist), wird der Name als Variable "friend" gespeichert. "add_friend()" wird ausgeführt.
            # Der Empfänger der Nachricht wird durch das erste Element in der Liste repräsentiert,
            # das mit dem angegebenen "client"-Argument verknüpft ist und in der "clients"-Variable
            # gespeichert ist.



