from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow

from client.gui.game import GamePage
from client.gui.login import LoginPage
from client.gui.matches import MatchingPage
from client.network import NetworkClientBase


class HandlerWindow(QMainWindow):
    def __init__(self, options=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Battleship")
        self.setWindowIcon(QIcon("client/assets/icon.png"))

        self.connection = NetworkClientBase()

        self.defaults = {
            "login": LoginPage,
            "matching": MatchingPage,
            "game": GamePage
        }

        self.pages = {
            "login": LoginPage(),
            "matching": MatchingPage(),
            "game": GamePage()
        }

        self.match_timer = QTimer()
        self.game_timer = QTimer()

        self.current_page = None
        if len(options) == 3:
            self.connection.connect(options[1], options[2])
            self.set_page("matching")
        else:
            self.set_page("login")

    def set_page(self, page: str):
        if self.current_page:
            self.pages[self.current_page].parent = None
            self.pages[self.current_page] = self.defaults[self.current_page]()
        self.current_page = page
        self.setCentralWidget(self.pages[page])
        self.pages[page].init()

    def connect(self, username: str, password: str):
        return self.connection.connect(username, password)