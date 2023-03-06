from functools import partial

from PyQt6.QtWidgets import QGridLayout, QPushButton, QLabel

from client.ships import *


class Space(QPushButton):
    def __init__(self, pos, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position = pos
        self.ship = ""
        self.hit = False
        self.stlye = {"background-color": "white", "color": "black", "border": "1px solid black", "padding": "2",
                      "margin": "2"}
        self.setFixedSize(25, 25)
        self.clicked.connect(self.button_clicked)
        self.update()

    def update(self) -> None:
        if self.hit:
            self.setText("X")
        else:
            self.setText("")
        self.setStyleSheet("; ".join([f"{key}: {value}" for key, value in self.stlye.items()]))

    def button_clicked(self):
        self.parent().place_ship(self.position)


class Field(QGridLayout):
    def __init__(self, own: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.own: bool = own

        self.ships = []

        self.field = []
        self.field_representation = []
        self.clickable = True

        self.setSpacing(0)

        self.reset_field()

    def reset_field(self):
        # remove all widgets
        for i in reversed(range(self.count())):
            self.itemAt(i).widget().setParent(None)

        self.field = []

        for i in range(12):
            self.field.append([])
            for j in range(12):
                spc = Space((i, j))
                self.addWidget(spc, i, j)
                self.field[i].append(spc)

    def update_field(
            self,
            field: list[list[str]],
            ships: list[Ship] = None,
            highlight: Ship = None,
            position: tuple[int, int] = None):
        self.field_representation = field
        for i in range(12):
            for j in range(12):
                if field[i][j] == "X":
                    self.field[i][j].hit = True
                    self.field[i][j].stlye["border"] = "1px solid black"
                elif field[i][j] == "-":
                    self.field[i][j].hit = True
                    self.field[i][j].stlye["border"] = "1px solid red"
                else:
                    self.field[i][j].ship = ""
                    self.field[i][j].hit = False
                    self.field[i][j].stlye["border"] = "1px solid black"
                    self.field[i][j].stlye["background-color"] = "white"

                self.field[i][j].update()

        if ships is not None:
            self.update_ships(*ships, highlight=highlight, position=position)

    def update_ships(self, *ships: Ship, highlight: Ship = None, position: tuple[int, int] = None):
        for ship in ships:
            for x, y in ship.ship_parts:
                self.field[x][y].ship = ship.name
                self.field[x][y].stlye["border"] = "1px solid black"
                if highlight:
                    if ship.coords == highlight.coords:
                        if not position:
                            self.field[x][y].stlye["background-color"] = "green"
                        else:
                            continue
                    else:
                        self.field[x][y].stlye["background-color"] = "blue" if ship.amount != ship.hits else "black"
                else:
                    self.field[x][y].stlye["background-color"] = "blue" if ship.amount != ship.hits else "black"
                self.field[x][y].update()
        if position and highlight:
            print(highlight.ship_parts)
            ship = highlight.new_ship(position)
            print(ship.ship_parts)
            for x, y in ship.ship_parts:
                self.field[x][y].ship = ship.name
                self.field[x][y].stlye["border"] = "1px solid black"
                self.field[x][y].stlye["background-color"] = "green"
                self.field[x][y].update()
        self.ships = ships


class Placing(QGridLayout):
    def __init__(self):
        super().__init__()
        self.setSpacing(0)
        self.own_ships = []
        self.enemy_ships = []

    def update_ships(self, own_ships: list[Ship], enemy_ships: list[Ship]):
        # remove all the widgets
        for i in reversed(range(self.count())):
            self.itemAt(i).widget().setParent(None)

        lbl = QLabel("Own ships")
        lbl.setStyleSheet("font-size: 15px")
        lbl.setFixedSize(100, 20)
        self.addWidget(lbl, 0, 0)

        lbl = QLabel("Enemy ships")
        lbl.setStyleSheet("font-size: 15px")
        lbl.setFixedSize(100, 20)
        self.addWidget(lbl, 0, 1)

        for index, ship in enumerate(self.own_ships, 1):
            btn = QPushButton(ship.name)
            btn.clicked.connect(partial(self.ship_selected, ship))
            btn.setStyleSheet(
                f"background-color: {'white' if ship.amount != ship.hits else 'red'}; color: black;"
                f"border: 1px solid black; padding: 2; margin: 2"
            )
            self.addWidget(btn, index, 0)

        for index, ship in enumerate(self.enemy_ships, 1):
            btn = QPushButton(ship.name)
            btn.setStyleSheet(
                f"background-color: {'white' if ship.amount != ship.hits else 'red'}; color: black;"
                f"border: 1px solid black; padding: 2; margin: 2"
            )
            self.addWidget(btn, index, 1)

        self.own_ships = own_ships
        self.enemy_ships = enemy_ships

    def ship_selected(self, ship: Ship):
        game_page: "GamePage" = self.parent().parent().parent()
        if game_page.positioning:
            game_page.selected = ship
            game_page.own.update_ships(*game_page.own.ships, highlight=ship, position=game_page.position)
