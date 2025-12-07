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

        # === SCÈNE ===
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
        self.max_avions = 10

        # pixmap de base
        self.base_pixmap = QPixmap("assets/avions/avion_jet_orange.png").scaled(60, 60)

        # === TIMERS ===
        self.last_time = time.time()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(30)

        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.spawn_avion)
        self.spawn_timer.start(5000)

        # === PAUSE ===
        self.en_pause = False

        # focus clavier
        self.setFocusPolicy(Qt.StrongFocus)

        # ✅ sélection souris
        self.scene.selectionChanged.connect(self.selection_changed)
        # === RECOMMENCER ===
        if hasattr(self, "btnRecommencer"):  # ou "recommencer" selon le nom dans ton .ui
            self.btnRecommencer.clicked.connect(self.recommencer)
        # === CONNEXIONS BOUTONS AVIONS ===
        if hasattr(self, "monter"):
            self.monter.clicked.connect(self.monter_relay)
        if hasattr(self, "descendre"):
            self.descendre.clicked.connect(self.descendre_relay)
        if hasattr(self, "accelerer"):
            self.accelerer.clicked.connect(self.accelerer_relay)
        if hasattr(self, "decelerer"):
            self.decelerer.clicked.connect(self.deceler_relay)
        if hasattr(self, "atterrir"):
            self.atterrir.clicked.connect(self.atterrir_relay)

        # === PAUSE / REPRENDRE (UN SEUL BOUTON) ===
        if hasattr(self, "pause"):
            self.pause.clicked.connect(self.pause_toggle)
            self.pause.setText("Pause")

        # === QUITTER ===
        if hasattr(self, "btnQuitter"):
            self.btnQuitter.clicked.connect(self.quitter_relay)
        # === TIMER DE NIVEAU ===
        self.temps_ecoule = 0  # en secondes
        self.niveau_timer = QTimer()
        self.niveau_timer.timeout.connect(self.update_niveau)
        self.niveau_timer.start(1000)  # toutes les secondes
    # -------------------------
    # QUITTER
    # -------------------------
    def quitter_relay(self):
        QApplication.quit()

    # -------------------------
    # SPAWN AVION
    # -------------------------
    def spawn_avion(self):
        if len(self.avions) >= self.max_avions or self.en_pause:
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

        item.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        item.setFlag(QGraphicsPixmapItem.ItemIsFocusable, True)

        self.scene.addItem(item)
        self.avions.append(avion)
        self.plane_items.append(item)

    # -------------------------
    # UPDATE
    # -------------------------
    def update_game(self):
        if self.en_pause:
            return

        now = time.time()
        dt = min(now - self.last_time, 0.05)
        self.last_time = now

        avions_a_supprimer = []
        items_a_supprimer = []

        for avion, item in zip(self.avions, self.plane_items):
            avion.update_position(dt)

            x, y = avion.position
            item.setPos(x, y)
            item.setRotation(avion.cap - 270)

            # ✅ Mise à jour de l’icône si elle change
            if not hasattr(avion, "icone_affichee") or avion.icone_affichee != avion.icone:
                pix = QPixmap(avion.icone)
                if pix.isNull():
                    pix = self.base_pixmap
                item.setPixmap(pix.scaled(60, 60))
                avion.icone_affichee = avion.icone

            # ✅ Marquage pour suppression
            if avion.etat in ["crash", "atterri"]:
                avions_a_supprimer.append(avion)
                items_a_supprimer.append(item)

        # ✅ Suppression réelle après la boucle
        for avion, item in zip(avions_a_supprimer, items_a_supprimer):
            self.avions.remove(avion)
            self.plane_items.remove(item)
            self.scene.removeItem(item)

            if self.avion_en_cours == avion:
                self.avion_en_cours = None

        # ✅ Vérification des collisions
        fin_du_jeu = verifier_toutes_les_collisions(self.avions)
        if fin_du_jeu:
            print("FIN DE PARTIE")
            self.timer.stop()
            self.spawn_timer.stop()

        # ✅ Mise à jour des infos sélectionnées
        self.afficher_infos_avion()

    # ✅ MAJ INFOS EN DIRECT

    # -------------------------
    # SÉLECTION SOURIS
    # -------------------------
    def selection_changed(self):
        items = self.scene.selectedItems()

        if not items:
            self.avion_en_cours = None
            self.afficher_infos_avion()
            return

        item = items[0]

        if item in self.plane_items:
            index = self.plane_items.index(item)
            self.avion_en_cours = self.avions[index]
            print(f"✈ Avion {self.avion_en_cours.id} sélectionné")
            self.afficher_infos_avion()

    # -------------------------
    # AFFICHAGE INFOS AVION ✅
    # -------------------------
    def afficher_infos_avion(self):
        if not self.avion_en_cours:
            if hasattr(self, "altitude"):
                self.altitude.setText("—")
                self.carburant.setText("—")
                self.vitesse.setText("—")
            return

        a = self.avion_en_cours

        if hasattr(self, "altitude"):
            self.altitude.setText(f"{int(a.altitude)} m")
            self.carburant.setText(f"{int(a.carburant)} %")
            self.vitesse.setText(f"{int(a.vitesse)} km/h")

    # -------------------------
    # RELAYS AVIONS
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

    def deceler_relay(self):
        if self.avion_en_cours:
            self.avion_en_cours.decelerer()

    def atterrir_relay(self):
        if self.avion_en_cours:
            self.avion_en_cours.atterrir()

    # -------------------------
    # PAUSE / REPRENDRE
    # -------------------------
    def pause_toggle(self):
        if not self.en_pause:
            self.en_pause = True
            self.timer.stop()
            self.spawn_timer.stop()
            self.niveau_timer.stop()  # ✅ AJOUTER
            if hasattr(self, "pause"):
                self.pause.setText("Reprendre")
            print("JEU EN PAUSE")
        else:
            self.en_pause = False
            self.last_time = time.time()
            self.timer.start(30)
            self.spawn_timer.start(5000)
            self.niveau_timer.start(1000)  # ✅ AJOUTER
            if hasattr(self, "pause"):
                self.pause.setText("Pause")
            print("JEU REPRIS")

    def recommencer(self):
        """Remet le jeu à zéro"""
        self.timer.stop()
        self.spawn_timer.stop()
        self.niveau_timer.stop()  # ✅ AJOUTER

        for item in self.plane_items:
            self.scene.removeItem(item)

        self.avions.clear()
        self.plane_items.clear()
        self.avion_en_cours = None
        self.afficher_infos_avion()
        self.next_id = 0

        self.temps_ecoule = 0  # ✅ RÉINITIALISER LE TIMER
        if hasattr(self, "timerNiveau"):
            self.timerNiveau.setText("00:00")

        self.en_pause = False
        if hasattr(self, "pause"):
            self.pause.setText("Pause")

        self.last_time = time.time()
        self.timer.start(30)
        self.spawn_timer.start(5000)
        self.niveau_timer.start(1000)  # ✅ REDÉMARRER

        print("🔄 JEU REDÉMARRÉ")

    def update_niveau(self):
        """Met à jour le timer de niveau"""
        if self.en_pause:
            return

        self.temps_ecoule += 1

        # Conversion en minutes:secondes
        minutes = self.temps_ecoule // 60
        secondes = self.temps_ecoule % 60

        # Affichage
        if hasattr(self, "timerNiveau"):  # ou le nom que tu donnes au label
            self.timerNiveau.setText(f"{minutes:02d}:{secondes:02d}")



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()