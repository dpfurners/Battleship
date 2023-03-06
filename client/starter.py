import sys

from PyQt6.QtWidgets import QApplication

from client.gui import HandlerWindow


def start():
    app = QApplication([])
    window = HandlerWindow(sys.argv)
    window.show()
    app.exec()
