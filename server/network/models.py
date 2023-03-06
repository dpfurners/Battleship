import socket
import threading
from dataclasses import dataclass, field


@dataclass
class Player:
    username: str
    socket: socket.socket
    addr: tuple[str, int]
    updater: threading.Thread
    matching: bool = field(default=True)
    wins: int = field(default=0)
    request_match: list["Player"] = field(default_factory=list)


@dataclass
class Game:
    player1: Player
    player2: Player
    player1_field: list[list[str]] = field(default_factory=lambda: [["" for _ in range(12)] for _ in range(12)])
    player1_ships: list["Ship"] = field(default_factory=list)
    player2_field: list[list[str]] = field(default_factory=lambda: [["" for _ in range(12)] for _ in range(12)])
    player2_ships: list["Ship"] = field(default_factory=list)
    still_positioning: bool = field(default=True)
    turn: bool = field(default=True)  # True = player1, False = player2

    @staticmethod
    def insert_ship(play_field: list[list[str]], ship: "Ship") -> list[list[str]]:
        for x, y in ship.ship_parts:
            play_field[x][y] = ship.name[0].lower()
        return play_field

    @staticmethod
    def validate_ship(play_field: list[list[str]], ship: "Ship") -> bool:
        for x, y in ship.ship_parts:
            if x < 0 or x > 11 or y < 0 or y > 11:
                return False
            try:
                if play_field[x][y] != "" or \
                        play_field[x][y + 1] != "" or \
                        play_field[x][y - 1] != "" or \
                        play_field[x + 1][y] != "" or \
                        play_field[x + 1][y + 1] != "" or \
                        play_field[x + 1][y - 1] != "" or \
                        play_field[x - 1][y] != "" or \
                        play_field[x - 1][y + 1] != "" or \
                        play_field[x - 1][y - 1] != "":
                    return False
            except IndexError:
                return False
        return True

    @staticmethod
    def hide(field: list[list[str]]) -> list[list[str]]:
        for i in range(12):
            for j in range(12):
                if field[i][j] != "X" and field[i][j] != "-":
                    field[i][j] = ""
        return field

