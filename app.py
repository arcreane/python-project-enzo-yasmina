import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem
)
from PySide6.QtGui import QColor,QPixmap
from PySide6.QtUiTools import loadUiType


Ui_MainWindow, BaseClass = loadUiType("mainwindow.ui")


class MainWindow(BaseClass, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Création de la scène sombre
        self.scene = QGraphicsScene(0, 0, 832, 480)
        self.scene.setBackgroundBrush(QColor(30, 30, 30))  # ZONE DE VOL SOMBRE

        # Association de la scène au GraphicsView
        self.Zonedevol.setScene(self.scene)

        # Création de la piste d'atterrissage blanche
        runway_width = 200
        runway_height = 30
        self.runway = QGraphicsRectItem(0, 0, runway_width, runway_height)
        self.runway.setBrush(QColor("white"))  # PISTE EN BLANC

        # Centrage de la piste
        x_center = (self.scene.width() - runway_width) / 2
        y_center = (self.scene.height() - runway_height) / 2
        self.runway.setPos(x_center, y_center)

        # Ajout dans la scène
        self.scene.addItem(self.runway)

        pixmap = QPixmap("assets/avions/avion_jet_orange.png").scaled(65,65)
        self.plane = QGraphicsPixmapItem(pixmap)
        self.plane.setPos(100, 100)
        self.scene.addItem(self.plane)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()



