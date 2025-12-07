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
        self.Zonedevol.setScene(self.scene)

        # piste
        self.runway = QGraphicsRectItem(0, 0, 200, 30)
        self.runway.setBrush(QColor("white"))
        self.runway.setPos(316, 225)
        self.scene.addItem(self.runway)

        # listes
        self.avions = []
        self.plane_items = []
        self.avion_en_cours = None

        # id auto
        self.next_id = 0

        # limite max avions
        self.max_avions = 10

        # pixmap de base
        self.base_pixmap = QPixmap("assets/avions/avion_jet_orange.png").scaled(60, 60)

        # timers
        self.last_time = time.time()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(30)

        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.spawn_avion)
        self.spawn_timer.start(5000)

        # focus clavier
        self.setFocusPolicy(Qt.StrongFocus)

        # ✅ sélection souris
        self.scene.selectionChanged.connect(self.selection_changed)

        # === Connexions boutons ===
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

    # -------------------------
    # SPAWN AVION
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

        pixmap = QPixmap(avion.icone)
        if pixmap.isNull():
            pixmap = self.base_pixmap

        pixmap = pixmap.scaled(60, 60)
        item = QGraphicsPixmapItem(pixmap)
        item.setTransformOriginPoint(30, 30)
        item.setPos(*avion.position)

        # ✅ sélection souris activée
        item.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        item.setFlag(QGraphicsPixmapItem.ItemIsFocusable, True)

        self.scene.addItem(item)

        self.avions.append(avion)
        self.plane_items.append(item)

    # -------------------------
    # UPDATE
    # -------------------------
    def update_game(self):
        now = time.time()
        dt = min(now - self.last_time, 0.05)
        self.last_time = now

        for avion, item in zip(self.avions, self.plane_items):
            avion.update_position(dt)

            x, y = avion.position
            item.setPos(x, y)
            item.setRotation(avion.cap - 270)

            if not hasattr(avion, "icone_affichee") or avion.icone_affichee != avion.icone:
                pix = QPixmap(avion.icone)
                if pix.isNull():
                    pix = self.base_pixmap
                item.setPixmap(pix.scaled(60, 60))
                avion.icone_affichee = avion.icone

        fin_du_jeu = verifier_toutes_les_collisions(self.avions)
        if fin_du_jeu:
            print("FIN DE PARTIE")
            self.timer.stop()
            self.spawn_timer.stop()

    # -------------------------
    # ✅ SÉLECTION SOURIS RÉELLE
    # -------------------------
    def selection_changed(self):
        items = self.scene.selectedItems()

        if not items:
            self.avion_en_cours = None
            print("Aucun avion sélectionné")
            return

        item = items[0]

        if item in self.plane_items:
            index = self.plane_items.index(item)
            self.avion_en_cours = self.avions[index]
            print(f"✈ Avion {self.avion_en_cours.id} sélectionné")

    # -------------------------
    # RELAYS BOUTONS
    # -------------------------
    def monter_relay(self):
        if self.avion_en_cours:
            self.avion_en_cours.monter()

    def descendre_relay(self):
        if self.avion_en_cours:
            self.avion_en_cours.descendre()

    def accelerer_relay(self):
        if self.avion_en_cours:
            self.avion_en_cours.accelerer()

    def decelerer_relay(self):
        if self.avion_en_cours:
            self.avion_en_cours.decelerer()

    def mettre_en_attente_relay(self):
        if self.avion_en_cours:
            self.avion_en_cours.mettre_en_attente()

    def reprendre_vol_relay(self):
        if self.avion_en_cours:
            self.avion_en_cours.reprendre_vol()

    def atterrir_relay(self):
        if self.avion_en_cours:
            self.avion_en_cours.atterrir()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
<