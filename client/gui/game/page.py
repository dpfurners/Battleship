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
                self.selected.direction = "horizontal" if self.selected.direction == "vertical" else "vertical"

    def game_update(self):
        self.parent().connection.send("get_update")
        new = self.parent().connection.recv()
        if isinstance(new, list):
            new = self.parent().connection.recv()
        elif isinstance(new, str):
            btn = QMessageBox.critical(self, "Login error", new)
            if btn == QMessageBox.StandardButton.Ok:
                self.parent().set_page("matching")
            return
        own_ships = new[2]
        if self.selected:
            for ship in own_ships:
                if ship.coords == self.selected.coords:
                    self.selected = ship
                    break
        self.own.update_field(new[0], new[2], self.selected, self.position)
        print("\n")
        self.enemy.update_field(new[1])
        self.placing.update_ships(new[2], new[3])
        self.positioning = new[4]

    def place_ship(self, position: tuple[int, int]):
        if self.positioning:
            if self.selected:
                if self.validate_ship(self.own.field_representation, self.selected.new_ship(position)):
                    print("valid")
                    if self.position == position:
                        self.parent().connection.send(
                            f"place_ship\n{self.selected.coords}\n{self.position}\n{self.selected.direction}"
                        )
                        self.selected = None
                        self.position = None
                    else:
                        self.position = position

    @staticmethod
    def validate_ship(play_field: list[list[str]], ship: "Ship") -> bool:
        print("validation")
        print(play_field, ship)
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