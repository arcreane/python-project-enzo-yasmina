import sys
import time
import random
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


        self.runway = QGraphicsRectItem(0, 0, 200, 30)
        self.runway.setBrush(QColor("white"))
        self.runway.setPos(316, 225)
        self.scene.addItem(self.runway)


        self.avions = []
        self.plane_items = []


        self.base_pixmap = QPixmap("assets/avions/avion_jet_orange.png").scaled(60, 60)


        self.last_time = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(30)


        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.spawn_avion)
        self.spawn_timer.start(5000)  # 5 secondes


    def spawn_avion(self):
        if len(self.avions) >= 5:
            return

        avion = Avion(
            altitude=7000,
            carburant=100,
            vitesse=random.randint(20, 60),
            cap=random.randint(0, 360),
            id=len(self.avions),
            position=(
                random.randint(50, 780),
                random.randint(50, 430)
            ),
            altitude_limitesup=9000,
            altitude_limiteinf=5000,
            classe="jet",
            etat="en vol"
        )

        pixmap = QPixmap(avion.icone).scaled(60, 60)

        item = QGraphicsPixmapItem(pixmap)
        item.setTransformOriginPoint(pixmap.width() / 2, pixmap.height() / 2)
        item.setPos(*avion.position)

        self.scene.addItem(item)

        self.avions.append(avion)
        self.plane_items.append(item)


    def update_game(self):
        now = time.time()
        dt = min(now - self.last_time, 0.05)
        self.last_time = now

        for avion, plane_item in zip(self.avions, self.plane_items):
            avion.update_position(dt)

            x, y = avion.position
            plane_item.setPos(x, y)


            plane_item.setRotation(avion.cap - 270)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
