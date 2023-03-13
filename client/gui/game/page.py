from PyQt6.QtCore import QRect
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QBoxLayout, QMessageBox, QLabel
from PyQt6 import QtGui

from client.ships import *

from client.gui.game.field import Field, Placing


class GamePage(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QBoxLayout(QBoxLayout.Direction.LeftToRight, self)
        self.game = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.game.setSpacing(20)
        self.stats = QBoxLayout(QBoxLayout.Direction.TopToBottom)

        self.own: Field | None = None
        self.enemy: Field | None = None
        self.placing: Placing | None = None

        self.positioning: bool | None = None
        self.selected: Ship | None = None
        self.position: tuple[int, int] | None = None

        self.turn: bool | None = None

        self.image_label: QLabel | None = None
        self.images: list[QPixmap] | None = None

    def init(self):
        self.parent().setFixedSize(800, 600)
        self.parent().setWindowTitle("Battleship - Game")

        self.parent().game_timer.timeout.connect(self.game_update)
        self.parent().game_timer.start(1000)

        self.layout.addLayout(self.game)
        self.layout.addLayout(self.stats)

        self.enemy = Field(False)
        self.enemy.setGeometry(QRect(0, 0, 375, 375))
        self.own = Field()
        self.own.setGeometry(QRect(0, 400, 375, 375))
        self.game.addLayout(self.own)
        self.game.addLayout(self.enemy)

        self.placing = Placing()

        self.stats.addLayout(self.placing)
        self.stats.addWidget(QLabel("Aircraft Carrier"))
        self.game_update()

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == 82:
            if self.selected:
                new = self.selected.new_ship(
                    self.selected.coords,
                    "horizontal" if self.selected.direction == "vertical" else "vertical")
                if self.validate_ship(self.own.field_representation, new, self.selected):
                    self.selected = new
                    self.own.update_field(self.own.field_representation, self.own.ships, new, self.position)

    def game_update(self):
        self.parent().connection.send("get_update")
        new = self.parent().connection.recv()
        # Der client bekommt folgende Daten:
        # - Das eigene Spielfeld
        # - Das gegnerische Spielfeld (Ohne die Positionen der Schiffe)
        # - Die eigenen Schiffe
        # - Die gegnerischen Schiffe (als Dummy-Objekte -> ohne Position)
        # - Ob die Positionierung von dir noch läuft
        # - Ob die Positionierung von dem anderen Spieler noch läuft
        # - Ob es der eigene Zug ist
        # - Ob das Spiel beendet ist
        # - Ob du das Spiel gewonnen hast
        if isinstance(new, list):
            new = self.parent().connection.recv()
        elif isinstance(new, str):
            btn = QMessageBox.critical(self, "Login error", new)
            if btn == QMessageBox.StandardButton.Ok:
                self.parent().set_page("matching")
            return
        own_field, other_field, own_ships, other_ships, own_positioning, other_positioning, turn, done, winner = new
        if done:
            if winner:
                QMessageBox.information(self, "Game over", "You won!")
            else:
                QMessageBox.information(self, "Game over", "You lost!")
            self.parent().game_timer.stop()
            self.parent().set_page("matching")
            return
        if self.selected:
            for ship in own_ships:
                if ship.coords == self.selected.coords and ship.direction == self.selected.direction:
                    self.selected = ship
                    break
        self.own.update_field(own_field, own_ships, self.selected, self.position)
        self.enemy.update_field(other_field)
        self.placing.update_ships(own_ships, other_ships)
        self.turn = turn
        self.positioning = own_positioning

        if own_positioning or other_positioning:
            self.placing.update_positioning(own_positioning, other_positioning)
        else:
            self.placing.update_turn(turn)

    def done_positioning(self):
        self.parent().connection.send("done_positioning")

    def field_click(self, position: tuple[int, int], own: bool):
        if own:
            if self.positioning:
                if self.selected:
                    if self.validate_ship(
                            self.own.field_representation,
                            self.selected.new_ship(position, self.selected.direction),
                            self.selected):
                        if self.position == position:
                            self.parent().connection.send(
                                f"place_ship\n{self.selected.coords}\n{self.position}\n{self.selected.direction}"
                            )
                            self.selected = None
                            self.position = None
                        else:
                            self.position = position
        else:
            if not self.enemy.field[position[0]][position[1]].hit:
                if self.turn:
                    self.enemy.field[position[0]][position[1]].hit = True
                    self.parent().connection.send(f"shoot\n{position}")

    def validate_ship(self, play_field: list[list[str]], ship: "Ship", old_ship: "Ship") -> bool:
        for x, y in ship.ship_parts:
            if x < 0 or x > 11 or y < 0 or y > 11:
                return False
            if not self.check_coord(x, y, play_field, old_ship):
                return False
        return True

    @staticmethod
    def check_coord(x: int, y: int, play_field: list[list[str]], old_ship: "Ship") -> bool:
        coord_checks = (
            (x, y), (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1),
            (x - 1, y + 1))
        old_ship_checks = [
            [(x, y), (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1),
             (x - 1, y + 1)] for x, y in old_ship.ship_parts]
        old_ship_checks = list(set(sum(old_ship_checks, [])))
        for coord in coord_checks:
            if coord in old_ship_checks:
                continue
            try:
                if play_field[coord[0]][coord[1]] != "":
                    return False
            except IndexError:
                # Ship is placed on the edge of the field
                if 0 > x > 11 and 0 > y > 11:
                    return False
        return True
