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

        self.pixmap = QPixmap("assets/avions/avion_jet_orange.png").scaled(60, 60)


        self.last_time = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(30)


        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.spawn_avion)
        self.spawn_timer.start(5000)  # 1 avion / 1,2 s



    def spawn_avion(self):
        if len(self.avions) >= 5:  #  MAX 5 avions
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

        item = QGraphicsPixmapItem(self.pixmap)
        item.setTransformOriginPoint(
            self.pixmap.width() / 2,
            self.pixmap.height() / 2
        )
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



            alt_min = avion.altitude_limiteinf
            alt_max = avion.altitude_limitesup
            alt = avion.altitude

            facteur = 0.5 + (alt - alt_min) / (alt_max - alt_min) * 0.8
            taille_base = 60
            nouvelle_taille = int(taille_base * facteur)

            pixmap = QPixmap("assets/avions/avion_jet_orange.png").scaled(
                nouvelle_taille,
                nouvelle_taille
            )

            plane_item.setPixmap(pixmap)


            plane_item.setTransformOriginPoint(
                pixmap.width() / 2,
                pixmap.height() / 2
            )


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
