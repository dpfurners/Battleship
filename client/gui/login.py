from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit, QLabel, QWidget, QGridLayout, QPushButton, QMessageBox


class MyInput(QLineEdit):
    def __init__(self, password: bool = False, *args, **kwargs):
        """
        Initialize the Input Field that updates the text attribute on every change
        and change the EchoMode to Password if the password flag is set
        """
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.on_text_changed)
        if password:
            self.setEchoMode(QLineEdit.EchoMode.Password)

    def on_text_changed(self, text):
        self.text = text


class MyLabel(QLabel):
    def __init__(self, text: str, *args, **kwargs):
        """Initialize the Label with a bigger Font Size"""
        super().__init__(text, *args, **kwargs)

        font = self.font()
        font.setPointSize(18)
        self.setFont(font)


class LoginPage(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QGridLayout(self)
        # self.parent().setFixedSize(100, 100)

        # Setup the Input Fields and the Labels
        self.username = MyInput()
        self.username_label = MyLabel("Name")

        self.password = MyInput(True)
        self.password_label = MyLabel("Password")

        # Setup the Buttons to Cancel or Accept the Login
        self.cancel = QPushButton("Cancel")
        self.cancel.clicked.connect(self._cancel)

        self.accept = QPushButton("Login")
        self.accept.clicked.connect(self._login)

    def init(self):
        # Add the Widgets to the Layout with the right position in the grid layout
        # AlignRight is a flag to align the text to the right side
        self.layout.addWidget(self.username_label, 0, 0, Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.username, 0, 1)
        self.layout.addWidget(self.password_label, 2, 0, Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.password, 2, 1)
        self.layout.addWidget(self.cancel, 4, 0)
        self.layout.addWidget(self.accept, 4, 1)

    def _cancel(self):
        self.parent().close()

    def _login(self):
        conn = self.parent().connect(self.username.text, self.password.text)
        if conn is True:
            self.parent().set_page("matching")
            return

        self.username.setText("")
        self.password.setText("")
        btn = QMessageBox.critical(self, "Login error", conn)
        if btn == QMessageBox.StandardButton.Ok:
            self.parent().connection.reset()