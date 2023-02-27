import sys
from PyQt6.QtWidgets import *

class BattleshipWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Battleship Game")
        self.setGeometry(100, 100, 800, 600)

        # Hauptwidget erstellen und Layout definieren
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # Eigene See Widget erstellen
        own_sea_widget = QWidget()
        own_sea_layout = QGridLayout()
        own_sea_layout.setSpacing(5)  
        own_sea_widget.setLayout(own_sea_layout)
        own_sea_label = QLabel("Own Sea")
        own_sea_layout.addWidget(own_sea_label, 0, 0)
        
        spacer_item = QSpacerItem(20, 40, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        own_sea_layout.addItem(spacer_item, 1, 0)
        for i in range(10):
            for j in range(10):
                button = QPushButton()
                button.setFixedSize(40, 40)
                own_sea_layout.addWidget(button, i+2, j+1)

        # Rahmen um Own Sea Widget hinzufügen
        own_sea_frame = QFrame()
        own_sea_frame.setFrameShape(QFrame.Shape.Box)
        own_sea_frame.setFrameShadow(QFrame.Shadow.Plain)
        own_sea_layout_outer = QVBoxLayout()
        own_sea_layout_outer.addWidget(own_sea_widget)
        own_sea_frame.setLayout(own_sea_layout_outer)

        # Feindliche See Widget erstellen
        enemy_sea_widget = QWidget()
        enemy_sea_layout = QGridLayout()
        enemy_sea_layout.setSpacing(5)  # Set spacing between buttons
        enemy_sea_widget.setLayout(enemy_sea_layout)
        enemy_sea_label = QLabel("Enemy Sea")
        enemy_sea_layout.addWidget(enemy_sea_label, 0, 0)
        
        spacer_item = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        enemy_sea_layout.addItem(spacer_item, 1, 0)
        for i in range(10):
            for j in range(10):
                button = QPushButton()
                button.setFixedSize(40, 40)
                enemy_sea_layout.addWidget(button, i+1, j)

        # Rahmen um Enemy Sea Widget hinzufügen
        enemy_sea_frame = QFrame()
        enemy_sea_frame.setFrameShape(QFrame.Shape.Box)
        enemy_sea_frame.setFrameShadow(QFrame.Shadow.Plain)
        enemy_sea_layout_outer = QVBoxLayout()
        enemy_sea_layout_outer.addWidget(enemy_sea_widget)
        enemy_sea_frame.setLayout(enemy_sea_layout_outer)

        # Statistik Widget erstellen
        statistics_widget = QGroupBox("Statistics")
        statistics_layout = QVBoxLayout()
        statistics_widget.setLayout(statistics_layout)
        statistics_label = QLabel("Number of Ships: 3")
        statistics_layout.addWidget(statistics_label)

        # Widgets zum Hauptlayout hinzufügen
        main_layout.addWidget(own_sea_frame)
        main_layout.addWidget(enemy_sea_frame)
        main_layout.addWidget(statistics_widget)

        # Hauptwidget zum Fenster hinzufügen
        self.setCentralWidget(main_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BattleshipWindow()
    window.show()
    sys.exit(app.exec())