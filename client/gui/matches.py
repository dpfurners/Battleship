from functools import partial

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QPushButton, QLabel, QBoxLayout, QMessageBox


class MatchingPage(QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available = []

        self.widgt = QWidget()
        self.layout = QVBoxLayout(self.widgt)
        self.setLayout(self.layout)

        self.setWidget(self.widgt)

    def init(self):
        self.parent().match_timer.timeout.connect(self.matching_update)
        self.parent().match_timer.start(1000)
        self.matching_update()
        self.parent().setFixedSize(400, 400)
        self.setWidgetResizable(False)
        self.parent().setWindowTitle("Battleship - Matching")

        self.update()

    def update(self):
        self.widgt = QWidget()
        self.layout = QVBoxLayout(self.widgt)

        if self.available:
            for client in self.available:
                btn = QPushButton(self)
                btn.setFixedSize(360, 35)
                btn_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
                btn_label = QLabel(client[0], self)
                btn_label.setStyleSheet("text-align: right; padding-right: 5px")
                btn_layout.addWidget(btn_label)
                btn_layout.addWidget(QLabel(f"Games: {client[1]}", self))
                btn_layout.addWidget(QLabel(f"Win/Lose Ratio: {client[4]} - {client[2]}/{client[3]}", self))
                style_sheet = f"background-color: {'green' if client[5] else 'red'}; " \
                              f"color: {'green' if client[6] else 'black'};"
                btn.setLayout(btn_layout)
                btn.setStyleSheet(style_sheet)
                btn.clicked.connect(partial(self.parent().connection.send, f"match\n{client[0]}"))
                self.layout.addWidget(btn)
            self.setWidget(self.widgt)

        else:
            lbl = QLabel("No matches available")
            lbl.setStyleSheet("margin: 10px;")
            self.setWidget(lbl)

    def matching_update(self) -> None:
        try:
            self.parent().connection.send("get_available")
        except ConnectionResetError:
            self.parent().set_page("login")
            self.parent().connection.close()
            return
        # Der Spieler erhält mehrere dieser "tuples" in einer Liste und in einem "tuple" sind folgende
        # Informationen:
        # 0. Der Benutzername
        # 1. Die Anzahl der Spiele
        # 2. Die Anzahl der Siege
        # 3. Die Anzahl der Niederlagen
        # 4. Die Win/Lose Ratio
        # 5. Ob der Client ein Match mit dem Spieler hat
        # 6. Ob der Spieler ein Match mit dem Client hat
        new = self.parent().connection.recv()
        if new == "game":
            self.parent().match_timer.stop()
            self.parent().set_page("game")
            return
        self.available = new
        self.update()