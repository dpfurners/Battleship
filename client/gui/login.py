from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *  # Importiert alle QtWidgets von PyQt6
from client.network import NetworkClientBase


# --Erstellt eine Klasse Window, die das Fenster genau beschreibt und aus der ein Objekt erstellt werden kann.
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.client = NetworkClientBase("localhost", 1234)
        # --QGridLayout ist eine Klasse, mit der ein gerastertes Layout mit Zeilen und Spalten erstellt werden kann, in denen verschiedene Widgets eingesetzt werden können.
        layout = QGridLayout()
        #--Setzt den Namen des Fensters
        self.setWindowTitle("Battleship")
        self.setLayout(layout)

        # ---Texte---
        # --Hier wird ein Objekt (user) aus der Klasse QLabel erstellt, mit der ein Text im Fenster angezeigt werden kann.
        user = QLabel("Username")
        # --Hier wird die Schriftgröße von user auf 18 eingestellt.
        font = user.font()
        font.setPointSize(18)
        user.setFont(font)
        # --Hier wird user in das GridLayout positioniert (Objekt, Zeile, Spalte, Länge nach unten, Länge nach Rechts, Rechtsbündig).
        layout.addWidget(user, 0, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignRight)

        # --Hier folgt der gleiche Prozess mit Passwort
        password = QLabel("Passwort")
        font = password.font()
        font.setPointSize(18)
        password.setFont(font)
        layout.addWidget(password, 2, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignRight)

        # ---Eingabefelder---
        # --Hier wird ein Objekt (input1) aus der Klasse QLineEdit erstellt, mit der ein Eingabefeld im Fenster angezeigt werden kann.
        self.input1 = QLineEdit()
        # --Hier wird input1 in das GridLayout positioniert (Objekt, Zeile, Spalte).
        layout.addWidget(self.input1, 0, 5)

        # --Hier folgt der gleiche Prozess mit input3
        self.input3 = QLineEdit()
        self.input3.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.input3, 2, 5)

        # ---Eingabefelder---

        # ---Knöpfe---
        # --Hier wird ein Objekt (button1) aus der Klasse QPushButton erstellt, mit der ein Knopf im Fenster angezeigt werden kann.
        button1 = QPushButton("Abbrechen")
        # --Hier löst der Knopf ein Event aus, wenn er gedrückt wurde: self.close = das Fenster schließt sich
        button1.clicked.connect(self.close)
        # --Hier wird button1 in das GridLayout positioniert (Objekt, Zeile, Spalte).
        layout.addWidget(button1, 6, 3)

        # --Hier folgt der gleiche Prozess mit button2
        button2 = QPushButton("OK")
        # --button2 löst das Event self.login aus: Die Methode login() wird aufgerufen.
        button2.clicked.connect(self.login)
        layout.addWidget(button2, 6, 5, alignment=Qt.AlignmentFlag.AlignRight)

    # ---Knöpfe---

    # ---Die Methode login() wird aufgerufen wenn der Knopf "OK" gedrückt wurde.
    def login(self):

        data = self.client.connect(self.input1.text(), self.input3.text())
        # --Die If-Anweisung überprüft die in die Eingabefelder eingegebenen Daten.
        if data:
            # --Wenn diese stimmen, wird es in der Konsole bekannt gegeben.
            print("Eingaben stimmen überein!")
        else:
            # --Wenn diese nicht stimmen, wird durch die Klasse QMessageBox das Fenster failed_window erscheinen.
            failed_window = QMessageBox(self)
            failed_window.setText("Die eingegebenen Daten stimmen nicht überein!")
            failed_window.exec()
