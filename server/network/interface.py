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
                username = data["username"]
                password = data["password"]
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
        # Empfängt Daten vom Client
        return pickle.loads(client.recv(1024))

    def send(self, data: any, client: socket.socket) -> None:
        # Sendet Daten an den Client
        client.send(pickle.dumps(data))


class Lobby:
    # Speichert Informationen über Spieler in der Lobby
    # handled Spiele und Match Requests
    def __init__(self, server: "NetworkServerWithLobby"):
        self.players: list[Player] = []
        self.games: list[Game] = []
        self.server: "NetworkServerWithLobby" = server
        # Spieler/Spiele werden als objekt in eine Liste gespeichert

    def get_player(self, username):
        # Gibt den Spieler mit dem Benutzernamen zurück
        players = [client for client in self.players if client.username == username]
        return players[0] if players else None

    def get_matches(self, username):
        # Gibt die Match Requests des Spielers zurück
        try:
            return self.get_player(username).request_match
        except AttributeError:
            return None

    def get_game(self, username):
        # Gibt das Spiel des Spielers zurück
        # prüft, ob der Spieler in einem Spiel ist und ob beide Spieler noch online sind
        games = [game for game in self.games if game.player1.username == username or game.player2.username == username]
        if games:
            game = games[0]
            if not self.get_player(game.player1.username) or not self.get_player(game.player2.username):
                self.games.remove(game)
                return False
            return game
        return False

    def add_player(self, username, sock: socket.socket, addr: tuple[str, int]):
        # Fügt den Spieler zur Lobby hinzu
        # Started einen Thread für den Spieler
        thread = threading.Thread(target=self.update, args=(username, sock))
        db_client = self.server.database.DB_GetUser(username)
        client = Player(username, sock, addr, thread,
                        games=db_client.games, wins=db_client.wins, loses=db_client.loses,
                        wl_ratio=db_client.wins if db_client.loses == 0 else round(db_client.wins / db_client.loses,2))
        self.players.append(client)
        thread.start()

    def remove_player(self, username):
        # Entfernt den Spieler aus der Lobby
        # entfernt das Spiel aus der Lobby da der Spieler nicht mehr online ist
        self.players.remove(self.get_player(username))
        game = self.get_game(username)
        for player in self.players:
            if self.has_match(player.username, username):
                self.remove_match(player.username, username)
        self.server.clients.pop(username)

    def add_match(self, username, friend):
        # Fügt einen Match Request hinzu
        self.players[
            self.players.index(self.get_player(username))
        ].request_match.append(self.get_player(friend))

    def remove_match(self, username, friend):
        # Entfernt einen Match Request
        try:
            self.players[
                self.players.index(self.get_player(username))
            ].request_match.remove(friend)
        except ValueError:
            pass

    def has_match(self, username, friend):
        # Überprüft, ob der Spieler einen Match mit dem Freund hat
        matches = self.get_matches(username)
        if matches:
            return friend in matches
        return False

    def update(self, username, sock: socket.socket):
        # Thread für den Spieler
        while True:
            try:
                # Daten vom Client werden empfangen
                data = pickle.loads(sock.recv(1024))
                # Spieldaten sowie der Spieler selbst werden geladen
                game = self.get_game(username)
                you = self.get_player(username)
                if data == "get_available":
                    # Der Client fragt nach verfügbaren Spielern

                    # Alle Spieler, die nicht der Client selbst sind, werden in eine Liste gespeichert
                    clients_ex_u = [client for client in self.players if client.username != username]
                    # Es wird nun alle Clients durchgegangen und überprüft, ob der Client
                    # mit einem anderen Client ein Match hat
                    # Falls ja, wird überprüft, ob schon ein Spiel gestartet wurde
                    # wenn nicht, wird ein Spiel gestartet
                    for client in clients_ex_u:
                        if self.has_match(client.username, username) and self.has_match(username, client.username):
                            if game and not game.done:
                                # Mit der nachricht "game" wird dem Client mitgeteilt, dass das Spiel gestartet wurde
                                sock.send(pickle.dumps("game"))
                                # Das Match wird entfernt da die Spieler nun in einem Spiel sind
                                self.remove_match(client.username, username)
                                self.remove_match(username, client.username)
                                self.server.database.DB_AddGame(username)
                                self.server.database.DB_AddGame(client.username)
                                game.player1.games += 1
                                game.player2.games += 1
                            else:
                                # Ein neues Spiel wird gestartet
                                gme = Game(client, you)
                                # Die Schiffe werden automatisch platziert
                                gme.player1_field, gme.player1_ships = self.automatic_ships()
                                gme.player2_field, gme.player2_ships = self.automatic_ships()
                                self.games.append(gme)
                                sock.send(pickle.dumps("game"))
                                print(f"[{'GAME':<15}] {gme.player1.username} vs {gme.player2.username} - started")
                            continue
                    # Der Spieler erhält mehrere dieser "tuples" in einer Liste und in einem "tuple" sind folgende
                    # Informationen:
                    # 0. Der Benutzername
                    # 1. Die Anzahl der Spiele
                    # 2. Die Anzahl der Siege
                    # 3. Die Anzahl der Niederlagen
                    # 4. Die Win/Lose Ratio
                    # 5. Ob der Client ein Match mit dem Spieler hat
                    # 6. Ob der Spieler ein Match mit dem Client hat
                    sock.send(
                        pickle.dumps([
                            (
                                client.username,
                                client.games,
                                client.wins,
                                client.loses,
                                client.wl_ratio,
                                self.has_match(client.username, username),
                                self.has_match(username, client.username)
                            )
                            for client in clients_ex_u
                        ])
                    )
                elif data.startswith("match"):
                    # Der Client möchte mit einem anderen Spieler ein Match starten
                    # wenn der Client bereits ein match mit dem Spieler hat, wird das match entfernt
                    # ansonsten wird das match hinzugefügt
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
                    # Wenn der Andere Spieler das Spiel verlässt, wird das Spiel beendet und der Client bekommt
                    # eine Nachricht, dass er gewonnen hat und er bekommt einen Sieg hinzugefügt
                    if game is False:
                        sock.send(pickle.dumps("The Player you were playing with disconnected\nYou won!"))
                        self.server.database.DB_AddWin(username)
                        you.wins = self.server.database.DB_GetUser(username).wins
                        you.wl_ratio = you.wins if you.loses == 0 else round(you.wins / you.loses, 2)
                        continue
                    # Der Client bekommt folgende Daten:
                    # 0. Das eigene Spielfeld
                    # 1. Das gegnerische Spielfeld (Ohne die Positionen der Schiffe)
                    # 2. Die eigenen Schiffe
                    # 3. Die gegnerischen Schiffe (als Dummy-Objekte -> ohne Position)
                    # 4. Ob die Positionierung von dir noch läuft
                    # 5. Ob die Positionierung von dem anderen Spieler noch läuft
                    # 6. Ob es der eigene Zug ist
                    # 7. Ob das Spiel beendet ist
                    # 8. Ob du das Spiel gewonnen hast
                    sock.send(pickle.dumps(
                        (
                            game.player1_field if game.player1 == you else game.player2_field,
                            game.player2_field if game.player1 == you else game.player1_field,
                            game.player1_ships if game.player1 == you else game.player2_ships,
                            [Dummy.from_ship(ship) for ship in game.player2_ships]
                            if game.player1 == you else [Dummy.from_ship(ship) for ship in game.player1_ships],
                            game.player1_positioning if game.player1 == you else game.player2_positioning,
                            game.player2_positioning if game.player1 == you else game.player1_positioning,
                            True if (game.turn and game.player1 == you) or (not game.turn and game.player2 == you) else False,
                            game.done,
                            True if game.winner == you else False
                        )))
                    if game.done:
                        if game.told:
                            self.games.remove(game)
                        else:
                            game.told = True
                elif data.startswith("place_ship"):
                    # Der Client möchte ein Schiff platzieren
                    # Die Daten werden in folgende Variablen gespeichert:
                    # old_pos → Die alte Position des Schiffes
                    # position → Die neue Position des Schiffes
                    # direction → Die Richtung des neuen Schiffes
                    old_pos, position, direction = data.split("\n")[1:]
                    # Macht die alte Position, die zuvor ein String war, zu einem Tuple
                    old_pos = tuple(map(int, old_pos.rstrip(")").lstrip("(").split(", ")))
                    # Macht die neue Position, die zuvor ein String war, zu einem Tuple
                    position = tuple(map(int, position.rstrip(")").lstrip("(").split(", ")))
                    ships = game.player1_ships if game.player1 == you else game.player2_ships
                    play_field = game.player1_field if game.player1 == you else game.player2_field
                    before_ship = ships[ships.index([ship for ship in ships if ship.coords == old_pos][0])]
                    new_ship = before_ship.new_ship(position, direction)
                    # Entfernt das alte Schiff vom Spielfeld
                    for part in before_ship.ship_parts:
                        play_field[part[0]][part[1]] = ""
                    # Prüft, ob das neue Schiff auf dem Spielfeld platziert werden kann,
                    # wenn ja, wird das neue Schiff platziert ansonsten wird das Spielfeld nicht verändert
                    if game.validate_ship(play_field, new_ship):
                        play_field = game.insert_ship(play_field, new_ship)
                        for ship in ships:
                            if ship.coords != old_pos:
                                play_field = game.insert_ship(play_field, ship)

                        if game.player1 == you:
                            game.player1_field = play_field
                            game.player1_ships[
                                game.player1_ships.index(before_ship)] = new_ship
                        else:
                            game.player2_field = play_field
                            game.player2_ships[
                                game.player2_ships.index(before_ship)] = new_ship
                elif data == "done_positioning":
                    # Der Client ist fertig mit der Positionierung
                    if game.player1 == you:
                        game.player1_positioning = False
                    else:
                        game.player2_positioning = False
                elif data.startswith("shoot"):
                    # Der Client möchte schießen
                    # Die Daten werden in folgende Variablen gespeichert:
                    # pos → Die Position, an der geschossen werden soll
                    # Die Position, die zuvor ein String war, wird zu einem Tuple umgewandelt
                    pos = tuple(map(int, data.split("\n")[1].rstrip(")").lstrip("(").split(", ")))
                    # Das Spielfeld, auf welches geschossen werden soll, wird ausgewählt
                    play_field = game.player2_field if game.player1 == you else game.player1_field
                    # Die Schiffe, die getroffen werden können, werden ausgewählt
                    ships = game.player2_ships if game.player1 == you else game.player1_ships
                    # Es wird "geschossen"
                    # Die Funktion wird mit den Daten aufgerufen und gibt das neue Spielfeld, die neuen Schiffe und
                    # ob ein Schiff getroffen wurde zurück
                    play_field, ships, hit = self.shoot(play_field, ships, pos)
                    # Die Spielfelder und Schiffe werden passend aktualisiert
                    if game.player1 == you:
                        game.player2_field = play_field
                        game.player2_ships = ships
                    else:
                        game.player1_field = play_field
                        game.player1_ships = ships
                    # Wenn ein Schiff getroffen wurde, ist derselbe Spieler dran, ansonsten ist der andere Spieler dran
                    if not hit:
                        game.turn = not game.turn
                    # Es wird überprüft, ob das Spiel beendet ist und die Daten werden aktualisiert
                    if self.check_win(game):
                        game.done = True
                        game.winner = game.player1 if game.player1 == you else game.player2
                        game.loser = game.player2 if game.player1 == you else game.player1
                        if game.player1 == you:
                            self.server.database.DB_AddWin(game.player1.username)
                            self.server.database.DB_AddLoss(game.player2.username)
                            game.player1.wins = self.server.database.DB_GetUser(username).wins
                            game.player1.wl_ratio = game.player1.wins if game.player1.loses == 0 else \
                                round(game.player1.wins / game.player1.loses, 2)
                            game.player2.loses = self.server.database.DB_GetUser(username).loses
                            game.player2.wl_ratio = game.player2.wins if game.player2.loses == 0 else \
                                round(game.player2.wins / game.player2.loses, 2)
                        else:
                            self.server.database.DB_AddWin(game.player2.username)
                            self.server.database.DB_AddLoss(game.player1.username)
                            game.player2.wins = self.server.database.DB_GetUser(username).wins
                            game.player2.wl_ratio = game.player2.wins if game.player2.loses == 0 else \
                                round(game.player2.wins / game.player2.loses, 2)
                            game.player1.loses = self.server.database.DB_GetUser(username).loses
                            game.player1.wl_ratio = game.player1.wins if game.player1.loses == 0 else \
                                round(game.player1.wins / game.player1.loses, 2)
                        print(f"[{'GAME':<15}] {game.player1.username} vs {game.player2.username} - "
                              f"{game.player1.username if game.player1 == game.winner else game.player2.username} won")
            # ConnectionResetError so wie EOFError werden abgefangen, da der Client disconnected
            # treten diese Fehler also auf, wird der Client aus der Liste der Spieler entfernt,
            # die Schleife wird beendet und im Terminal wird ausgegeben, dass der Client disconnected ist
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
        """
        Generates a random play field with ships
        """
        ships = []
        temp_play_field = [["" for _ in range(12)] for _ in range(12)]
        # Es werden 6 Schiffe generiert, die jeweils in einer Schleife platziert werden.
        # Dabei wird überprüft, ob das Schiff platziert werden kann
        # folgende Schiffe werden generiert: 3 Cruiser, 2 Frigate, 1 AircraftCarrier
        for ship in [Cruiser, Cruiser, Cruiser, Frigate, Frigate, AircraftCarrier]:
            shp = ship.new_ship((random.randint(0, 11), random.randint(0, 11)),
                                random.choice(["horizontal", "vertical"]))
            # Es werden neue Schiffe generiert, wenn das Schiff nicht platziert werden kann
            while not Game.validate_ship(temp_play_field, shp):
                shp = ship.new_ship((random.randint(0, 11), random.randint(0, 11)),
                                    random.choice(["horizontal", "vertical"]))
            else:
                # Eine passende Position für das Schiff wurde gefunden, das Schiff wird platziert
                ships.append(shp)
                temp_play_field = Game.insert_ship(temp_play_field, shp)
        return temp_play_field, ships

    def shoot(self,
              play_field: list[list[str]],
              ships: list["Ship"],
              position: tuple[int, int]) -> tuple[list[list[str]], list["Ship"], bool]:
        """A Player shoots at a position on the play field"""
        # Diese Variable wird benötigt, um zu überprüfen, ob ein Schiff getroffen wurde
        hit = False
        # Zuerst wird überprüft, ob an der Position ein Schiff ist oder ob bereits geschossen wurde
        if play_field[position[0]][position[1]] == "":
            play_field[position[0]][position[1]] = "X"
        # Wenn noch nicht auf das Schiff geschossen wurde, werden folgende Schritte ausgeführt
        else:
            # Jedes Schiff wird überprüft, ob es an der Position getroffen wurde
            for ship in ships:
                # Wenn das Schiff an der Position getroffen wurde, wird die Variable hit auf True gesetzt
                if position in ship.ship_parts:
                    ship.hits += 1
                    hit = True
                    break
            # Anschließend wird die Position auf dem Spielfeld mit einem "-" markiert
            play_field[position[0]][position[1]] = "-"
        return play_field, ships, hit

    def check_win(self, game: "Game") -> bool:
        """Checks if a player has won"""
        # Es wird überprüft, ob alle Schiffe des 1. Spielers getroffen wurden
        for ship in game.player1_ships:
            # Wenn ein Schiff noch nicht vollständig getroffen wurde, wird kein True zurückgegeben
            if ship.hits != ship.amount:
                break
        else:
            return True
        # Es wird überprüft, ob alle Schiffe des 2. Spielers getroffen wurden
        for ship in game.player2_ships:
            # Wenn ein Schiff noch nicht vollständig getroffen wurde, wird kein True zurückgegeben
            if ship.hits != ship.amount:
                break
        else:
            return True
        return False


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
                username = data["username"]
                password = data["password"]
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