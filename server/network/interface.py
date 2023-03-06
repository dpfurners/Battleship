"""
In this File, the Network connection is defined.

It includes a class to allow clients to connect to the server,
store the clients as object and handle the communication between the server and the clients.

IMPORTANT: This is the only file that is used to access the network. (Only file with socket objects)
"""
import random
import socket
import pickle
import threading

from server.network.models import Player, Game
from server.ships import *


class NetworkServerBase:
    def __init__(self, host: str, port: int, database: "DBInterface") -> None:
        # Host und Port werden als Argumente akzeptiert
        self.addr = (host, port)
        self.conn: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.database: "DBInterface" = database
        # Instanzvariablen werden initialisiert

        self.bind(host, port)

    def bind(self, host: str, port: int) -> None:
        # Host und Port werden verbunden
        print(f"[{'NETWORK':<15}] Binding the server to {host}:{port}")
        self.conn.bind((host, port))
        self.conn.listen(100)

    def close(self) -> None:
        # Verbindung wird geschlossen
        print(f"[{'NETWORK':<15}] Closing the server")
        self.conn.close()

    def accept_new(self) -> None:
        print(f"[{'NETWORK':<15}] Accepting new connections (100)")
        # Verbindungen vom Clients werden angenommen
        while True:
            try:
                sock, addr = self.conn.accept()
                # Für jedes "amount" wird die Client verbindung angenommen
                data = self.recv(sock)
                # Datenstrom wird empfangen, vom "sock" gelsesn und decodiert
                username, password = data.split("-")
                # Benutzername und Passwort werden durch Trennen des Datenstroms
                # durch "-" extrahiert
                if username in self.clients:
                    self.send("username already exists", sock)
                    continue
                # Überprüft, ob der Benutzername schon vergeben ist
                LogIn = self.database.DB_LogIn(username, password)
                if not LogIn[0]:
                    if LogIn[1]:
                        self.send("wrong password", sock)
                        continue
                    # Überprüft, ob das Passwort stimmt
                    else:
                        LogIn = self.database.DB_SignIn(username, password)
                        if not LogIn:
                            self.send("something went wrong", sock)
                    # Falls alles stimmt, werden Benutzername und Passwort in die
                    # Datenbank gespeichert. Wenn ein Fehler auftaucht, wird es
                    # dem Client übermittelt
                self.clients[username] = [sock, addr]
                self.send("connected", sock)
                print(f"[{'NETWORK':<15}] {len(self.clients)}/100"
                      f" - \"{username}\" connected to the server from {addr} (Update Thread started)")
                # Wenn Benutzername und Passwort übereinstimmen, fügt der Server
                # den Benutzer zur Liste der Clients hinzu, sendet eine Bestätigung
                # an den Client und fügt den Benutzer zur Lobby hinzu.
            except OSError:
                break

    def recv(self, client: socket.socket) -> any:
        return pickle.loads(client.recv(1024))

    def send(self, data: any, client: socket.socket) -> None:
        client.send(pickle.dumps(data))


class Lobby:
    # Speichert Informationen über Spieler in der Lobby
    def __init__(self, server: "NetworkServerWithLobby"):
        self.players: list[Player] = []
        self.games: list[Game] = []
        self.server: "NetworkServerWithLobby" = server
        # Spieler/Spiele werden als objekt in eine Liste gespeichert

    def get_player(self, username):
        players = [client for client in self.players if client.username == username]
        return players[0] if players else None

    def get_matches(self, username):
        try:
            return self.get_player(username).request_match
        except AttributeError:
            return None

    def get_game(self, username):
        games = [game for game in self.games if game.player1.username == username or game.player2.username == username]
        if games:
            game = games[0]
            if not self.get_player(game.player1.username) or not self.get_player(game.player2.username):
                return False
            return game
        return False

    def add_player(self, username, sock: socket.socket, addr: tuple[str, int]):
        thread = threading.Thread(target=self.update, args=(username, sock))
        client = Player(username, sock, addr, thread)
        self.players.append(client)
        thread.start()

    def remove_player(self, username):
        for player in self.players:
            if self.has_match(player.username, username):
                self.remove_match(player.username, username)
        self.players.remove(self.get_player(username))
        self.server.clients.pop(username)

    def add_match(self, username, friend):
        self.players[
            self.players.index(self.get_player(username))
        ].request_match.append(self.get_player(friend))

    def remove_match(self, username, friend):
        try:
            self.players[
                self.players.index(self.get_player(username))
            ].request_match.remove(friend)
        except ValueError:
            pass

    def has_match(self, username, friend):
        matches = self.get_matches(username)
        if matches:
            return friend in matches
        return False

    def update(self, username, sock: socket.socket):
        while True:
            try:
                data = pickle.loads(sock.recv(1024))
                game = self.get_game(username)
                you = self.get_player(username)
                if data == "get_available":
                    # Check if there is a match
                    clients_ex_u = [client for client in self.players if client.username != username]
                    for client in clients_ex_u:
                        if self.has_match(client.username, username) and self.has_match(username, client.username):
                            if game:
                                sock.send(pickle.dumps("game"))
                            else:
                                gme = Game(client, you)
                                gme.player1_field, gme.player1_ships = self.automatic_ships()
                                gme.player2_field, gme.player2_ships = self.automatic_ships()
                                self.games.append(gme)
                                sock.send(pickle.dumps("game"))
                            continue
                    sock.send(
                        pickle.dumps([
                            (
                                client.username,
                                client.wins,
                                self.has_match(client.username, username),
                                self.has_match(username, client.username)
                            )
                            for client in clients_ex_u
                        ])
                    )
                elif data.startswith("match"):
                    try:
                        match_with = data.split("\n")[1]
                    except IndexError:  # Invalid match statement (\n) missing
                        continue
                    matches = self.players[
                        self.players.index(you)
                    ].request_match
                    if match_with not in matches:
                        matches.append(match_with)
                    else:
                        matches.remove(match_with)
                elif data == "get_update":
                    if game is False:
                        sock.send(pickle.dumps("The Player you were playing with disconnected\nYou won!"))
                        self.server.database.DB_GetWin(username)
                        continue
                    # Der client bekommt folgende Daten:
                    # - Das eigene Spielfeld
                    # - Das gegnerische Spielfeld (Ohne die Positionen der Schiffe)
                    # - Die eigenen Schiffe
                    # - Die gegnerischen Schiffe (als Dummy-Objekte -> ohne Position)
                    # - Ob die Positionierung noch läuft
                    # - Ob es der eigene Zug ist
                    sock.send(pickle.dumps(
                        (
                            game.player1_field if game.player1 == you else game.player2_field,
                            game.hide(game.player2_field) if game.player1 == you else game.hide(game.player1_field),
                            game.player1_ships if game.player1 == you else game.player2_ships,
                            [Dummy.from_ship(ship) for ship in game.player2_ships]
                            if game.player1 == you else [Dummy.from_ship(ship) for ship in game.player1_ships],
                            game.still_positioning,
                            game.turn and game.player1 == you,
                        )))
                elif data.startswith("place_ship"):
                    old_pos, position, direction = data.split("\n")[1:]
                    old_pos = tuple(map(int, old_pos.rstrip(")").lstrip("(").split(", ")))
                    position = tuple(map(int, position.rstrip(")").lstrip("(").split(", ")))
                    ships = game.player1_ships if game.player1 == you else game.player2_ships
                    play_field = game.player1_field if game.player1 == you else game.player2_field
                    before_ship = ships[ships.index([ship for ship in ships if ship.coords == old_pos][0])]
                    new_ship = before_ship.new_ship(position, direction)
                    for part in before_ship.ship_parts:
                        play_field[part[0]][part[1]] = ""
                    if game.validate_ship(play_field, new_ship):
                        print("validated", username, self.get_game(username).player1 == you)
                        play_field = self.get_game(username).insert_ship(play_field, new_ship)

                        if self.get_game(username).player1 == you:
                            self.get_game(username).player1_field = play_field
                            self.get_game(username).player1_ships[
                                self.get_game(username).player1_ships.index(before_ship)] = new_ship
                        else:
                            self.get_game(username).player2_field = play_field
                            self.get_game(username).player2_ships[
                                self.get_game(username).player2_ships.index(before_ship)] = new_ship
                        print("\n".join(list(map(str, self.get_game(username).player1_field))))
                        print("\n".join(list(map(str, self.get_game(username).player2_field))))
            except ConnectionResetError:
                try:
                    self.remove_player(username)
                except IndexError:
                    pass
                print(f"[{'DISCONNECTED':<15}] {len(self.players)}/100"
                      f" - \"{username}\" disconnected from the server")
                break
            except EOFError:
                try:
                    self.remove_player(username)
                except IndexError:
                    pass
                print(f"[{'DISCONNECTED':<15}] {len(self.players)}/100"
                      f" - \"{username}\" disconnected from the server")
                break

    @staticmethod
    def automatic_ships() -> tuple[list[list[str]], list[Ship]]:
        ships = []
        temp_play_field = [["" for _ in range(12)] for _ in range(12)]
        for ship in [Cruiser, Cruiser, Cruiser, Frigate, Frigate, AircraftCarrier]:
            shp = ship.new_ship((random.randint(0, 11), random.randint(0, 11)),
                                random.choice(["horizontal", "vertical"]))
            while not Game.validate_ship(temp_play_field, shp):
                shp = ship.new_ship((random.randint(0, 11), random.randint(0, 11)),
                                    random.choice(["horizontal", "vertical"]))
            else:
                ships.append(shp)
                temp_play_field = Game.insert_ship(temp_play_field, shp)
        return temp_play_field, ships


class NetworkServerWithLobby(NetworkServerBase):
    def __init__(self, host: str, port: int, database) -> None:
        super().__init__(host, port, database)

        self.lobby = Lobby(self)

    def accept_new(self) -> None:
        print(f"[{'NETWORK':<15}] Accepting new connections (100)")
        # Verbindungen vom Clients werden angenommen (threads für jeden erstellen)
        while True:
            try:
                sock, addr = self.conn.accept()
                # Für jedes "amount" wird die Client verbindung angenommen
                data = self.recv(sock)
                # Datenstrom wird empfangen, vom "sock" gelsesn und decodiert
                username, password = data.split("-")
                # Benutzername und Passwort werden durch Trennen des Datenstroms
                # durch "-" extrahiert
                if username in self.clients:
                    self.send("username already exists", sock)
                    continue
                # Überprüft, ob der Benutzername schon vergeben ist
                LogIn = self.database.DB_LogIn(username, password)
                if not LogIn[0]:
                    if LogIn[1]:
                        self.send("wrong password", sock)
                        continue
                    # Überprüft, ob das Passwort stimmt
                    else:
                        LogIn = self.database.DB_SignIn(username, password)
                        if not LogIn:
                            self.send("something went wrong", sock)
                    # Falls alles stimmt, werden Benutzername und Passwort in die
                    # Datenbank gespeichert. Wenn ein Fehler auftaucht, wird es
                    # dem Client übermittelt
                self.lobby.add_player(username, sock, addr)
                # Neuer Client wird in die Lobby gespeichert
                self.clients[username] = [sock, addr]
                self.send("connected", sock)
                # Thread wird gestartet und wartet auf Nachrichten
                print(f"[{'NETWORK':<15}] {len(self.clients)}/100"
                      f" - \"{username}\" connected to the server from {addr} (Update Thread started)")
                # Wenn Benutzername und Passwort übereinstimmen, fügt der Server
                # den Benutzer zur Liste der Clients hinzu, sendet eine Bestätigung
                # an den Client und fügt den Benutzer zur Lobby hinzu.
            except OSError:
                break