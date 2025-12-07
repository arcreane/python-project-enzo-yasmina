import sys
import time

from PySide6.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem
)
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtUiTools import loadUiType
from PySide6.QtCore import QTimer

from Avion import Avion

Ui_MainWindow, BaseClass = loadUiType("mainwindow.ui")


class MainWindow(BaseClass, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


        self.scene = QGraphicsScene(0, 0, 832, 480)
        self.scene.setBackgroundBrush(QColor(30, 30, 30))
        self.Zonedevol.setScene(self.scene)


        runway_width = 200
        runway_height = 30
        self.runway = QGraphicsRectItem(0, 0, runway_width, runway_height)
        self.runway.setBrush(QColor("white"))

        x_center = (self.scene.width() - runway_width) / 2
        y_center = (self.scene.height() - runway_height) / 2
        self.runway.setPos(x_center, y_center)

        self.scene.addItem(self.runway)


        self.avion = Avion(
            altitude=7000,
            carburant=100,
            vitesse=140,
            cap=0,
            id=1,
            position=(100, 200),
            altitude_limitesup=9000,
            altitude_limiteinf=5000,
            classe="jet",
            etat="en vol"
        )


        pixmap = QPixmap("assets/avions/avion_jet_orange.png")

        if pixmap.isNull():
            print("❌ ERREUR : image introuvable")
        else:
            pixmap = pixmap.scaled(60, 60)

        self.plane_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.plane_item)


        self.plane_item.setTransformOriginPoint(
            self.plane_item.boundingRect().center()
        )


        x, y = self.avion.position
        self.plane_item.setPos(x, y)


        self.last_time = time.time()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(30)

    def update_game(self):
        now = time.time()
        dt = min(now - self.last_time, 0.03)
        self.last_time = now

        self.avion.update_position(dt)

        x, y = self.avion.position

        w = self.plane_item.pixmap().width()
        h = self.plane_item.pixmap().height()

        min_x = 0
        min_y = 0
        max_x = self.scene.width() - w
        max_y = self.scene.height() - h

        rebond = False


        if x <= min_x or x >= max_x:
            self.avion.cap = 180 - self.avion.cap
            rebond = True


        if y <= min_y or y >= max_y:
            self.avion.cap = -self.avion.cap
            rebond = True


        if rebond:
            self.avion.cap %= 360


        x = max(min_x, min(x, max_x))
        y = max(min_y, min(y, max_y))
        self.avion.position = (x, y)

        self.plane_item.setPos(x, y)
        self.plane_item.setRotation(self.avion.cap - 270)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
