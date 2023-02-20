from client.gui.Login import Window
from PyQt6.QtWidgets import QApplication 

#--app, ein Objekt von QApplication, kümmert sich um die Anwendung.
app = QApplication([])

#--erstellt ein Objekt window aus der selbstbeschriebenen Klasse Window().
window = Window()

#--window.show() lässt das Fenster anzeigen.
window.show()

#--Startet den Event-Loop
app.exec()