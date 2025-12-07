import sys
import time
import random
from PySide6.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem
)
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtUiTools import loadUiType
from PySide6.QtCore import QTimer, Qt

from Avion import Avion, verifier_toutes_les_collisions


Ui_MainWindow, BaseClass = loadUiType("mainwindow.ui")


class MainWindow(BaseClass, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # === scène ===
        self.scene = QGraphicsScene(0, 0, 832, 480)
        self.scene.setBackgroundBrush(QColor(30, 30, 30))
        # Zonedevol doit être le nom du QGraphicsView dans ton UI
        self.Zonedevol.setScene(self.scene)

        # piste
        self.runway = QGraphicsRectItem(0, 0, 200, 30)
        self.runway.setBrush(QColor("white"))
        self.runway.setPos(316, 225)
        self.scene.addItem(self.runway)

        # listes
        self.avions = []
        self.plane_items = []

        # id auto
        self.next_id = 0

        # pixmap de base (fallback)
        self.base_pixmap = QPixmap("assets/avions/avion_jet_orange.png").scaled(60, 60)

        # timers
        self.last_time = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(30)  # ~33 FPS

        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.spawn_avion)
        self.spawn_timer.start(5000)  # 5s

        # focus clavier
        self.setFocusPolicy(Qt.StrongFocus)

        # === Connexions boutons (SI ils existent dans ton UI) ===
        # Les noms btnMonter etc doivent correspondre aux noms dans Qt Designer.
        # Si ton pote a d'autres noms, il suffit de remplacer les noms ici.
        if hasattr(self, "btnMonter"):
            self.btnMonter.clicked.connect(self.monter_relay)
        if hasattr(self, "btnDescendre"):
            self.btnDescendre.clicked.connect(self.descendre_relay)
        if hasattr(self, "btnAccelerer"):
            self.btnAccelerer.clicked.connect(self.accelerer_relay)
        if hasattr(self, "btnDecelerer"):
            self.btnDecelerer.clicked.connect(self.decelerer_relay)
        if hasattr(self, "btnAttente"):
            self.btnAttente.clicked.connect(self.mettre_en_attente_relay)
        if hasattr(self, "btnReprendre"):
            self.btnReprendre.clicked.connect(self.reprendre_vol_relay)
        if hasattr(self, "btnAtterrir"):
            self.btnAtterrir.clicked.connect(self.atterrir_relay)

        # limite max avions
        self.max_avions = 10

    # -------------------------
    # spawn
    # -------------------------
    def spawn_avion(self):
        if len(self.avions) >= self.max_avions:
            return

        classe = random.choice(["jet", "ligne", "cargo"])

        r = random.random()
        if r < 0.02:
            couleur = "rouge"
        elif r < 0.12:
            couleur = "orange"
        else:
            couleur = "vert"

        carburant = random.randint(60, 100)

        avion = Avion(
            altitude=random.randint(5500, 8500),
            carburant=carburant,
            vitesse=random.randint(150, 250),
            cap=random.randint(0, 360),
            id=self.next_id,
            position=(random.randint(50, 780), random.randint(50, 440)),
            altitude_limitesup=10000,
            altitude_limiteinf=3000,
            classe=classe,
            couleur=couleur,
            etat="en vol"
        )
        self.next_id += 1

        # création graphique unique
        pixmap = QPixmap(avion.icone)
        if pixmap.isNull():
            pixmap = self.base_pixmap
        pixmap = pixmap.scaled(60, 60)
        item = QGraphicsPixmapItem(pixmap)
        item.setTransformOriginPoint(30, 30)
        item.setPos(*avion.position)

        self.scene.addItem(item)
        self.avions.append(avion)
        self.plane_items.append(item)


    def update_game(self):
        now = time.time()
        dt = min(now - self.last_time, 0.05)
        self.last_time = now

        # update avions + icons
        for avion, item in zip(self.avions, self.plane_items):
            avion.update_position(dt)

            x, y = avion.position
            item.setPos(x, y)
            item.setRotation(avion.cap - 270)

            # mise à jour icône uniquement si changé (économie)
            if not hasattr(avion, "icone_affichee") or avion.icone_affichee != getattr(avion, "icone", ""):
                pix = QPixmap(getattr(avion, "icone", ""))
                if pix.isNull():
                    pix = self.base_pixmap
                item.setPixmap(pix.scaled(60, 60))
                avion.icone_affichee = avion.icone

        # collisions globales
        fin_du_jeu = verifier_toutes_les_collisions(self.avions)

        if fin_du_jeu:
            print("FIN DE PARTIE")
            self.timer.stop()
            self.spawn_timer.stop()


    def avion_selectionne(self):
        # pour l'instant on retourne le 1er avion s'il existe
        # plus tard on peut renvoyer l'avion sélectionné par la souris
        if self.avions:
            return self.avions[0]
        return None

    def monter_relay(self):
        a = self.avion_selectionne()
        if a:
            a.monter()

    def descendre_relay(self):
        a = self.avion_selectionne()
        if a:
            a.descendre()

    def accelerer_relay(self):
        a = self.avion_selectionne()
        if a:
            a.accelerer()

    def decelerer_relay(self):
        a = self.avion_selectionne()
        if a:
            a.decelerer()

    def mettre_en_attente_relay(self):
        a = self.avion_selectionne()
        if a:
            a.mettre_en_attente()

    def reprendre_vol_relay(self):
        a = self.avion_selectionne()
        if a:
            a.reprendre_vol()

    def atterrir_relay(self):
        a = self.avion_selectionne()
        if a:
            a.atterrir()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
