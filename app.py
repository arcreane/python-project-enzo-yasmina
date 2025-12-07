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

        # =========================
        # SCÈNE
        # =========================
        self.scene = QGraphicsScene(0, 0, 832, 480)
        self.scene.setBackgroundBrush(QColor(30, 30, 30))
        self.Zonedevol.setScene(self.scene)

        # =========================
        # PISTE
        # =========================
        runway_width = 200
        runway_height = 30
        self.runway = QGraphicsRectItem(0, 0, runway_width, runway_height)
        self.runway.setBrush(QColor("white"))

        x_center = (self.scene.width() - runway_width) / 2
        y_center = (self.scene.height() - runway_height) / 2
        self.runway.setPos(x_center, y_center)

        self.scene.addItem(self.runway)

        # =========================
        # AVION LOGIQUE
        # =========================
        self.avion = Avion(
            altitude=7000,
            carburant=100,
            vitesse=40,   # ✅ vitesse RÉDUITE
            cap=0,        # vers la droite
            id=1,
            position=(100, 200),
            altitude_limitesup=9000,
            altitude_limiteinf=5000,
            classe="jet",
            etat="en vol"
        )

        # =========================
        # AVION GRAPHIQUE (PNG)
        # =========================
        pixmap = QPixmap("assets/avions/avion_jet_orange.png")

        if pixmap.isNull():
            print("❌ ERREUR : image introuvable")
        else:
            pixmap = pixmap.scaled(60, 60)

        self.plane_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.plane_item)

        # ✅ CENTRAGE DU POINT DE ROTATION SUR L’ITEM
        self.plane_item.setTransformOriginPoint(
            self.plane_item.boundingRect().center()
        )

        # ✅ POSITION INITIALE SYNC AVEC L’AVION
        x, y = self.avion.position
        self.plane_item.setPos(x, y)

        # =========================
        # TIMER DE JEU
        # =========================
        self.last_time = time.time()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(30)  # 30 ms ≈ 33 FPS ✅


    def update_game(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        # ✅ MISE À JOUR LOGIQUE
        self.avion.update_position(dt)

        # ✅ MISE À JOUR GRAPHIQUE
        x, y = self.avion.position
        self.plane_item.setPos(x, y)

        # ✅ SYNCHRO ROTATION AVEC LE CAP
        self.plane_item.setRotation(self.avion.cap)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
