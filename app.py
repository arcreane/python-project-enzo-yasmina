import sys
import time
import random
from PySide6.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem,
    QDialog, QVBoxLayout, QPushButton, QLabel
)
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtUiTools import loadUiType
from PySide6.QtCore import QTimer, Qt

from Avion import Avion, verifier_toutes_les_collisions

Ui_MainWindow, BaseClass = loadUiType("mainwindow.ui")


class MenuDemarrage(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contrôleur Aérien - Choix de Difficulté")
        self.setFixedSize(450, 380)

        self.difficulte_choisie = "normal"  # par défaut

        layout = QVBoxLayout()

        # Titre
        titre = QLabel("🛫 Choisissez votre difficulté 🛬")
        titre.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        titre.setAlignment(Qt.AlignCenter)
        layout.addWidget(titre)

        # Boutons de difficulté
        btn_facile = QPushButton("😊 Facile\n(Avion toutes les 8s)")
        btn_facile.setStyleSheet("padding: 12px; font-size: 14px;")
        btn_facile.clicked.connect(lambda: self.choisir("facile"))
        layout.addWidget(btn_facile)

        btn_normal = QPushButton("✈️ Normal\n(Avion toutes les 5s)")
        btn_normal.setStyleSheet("padding: 12px; font-size: 14px;")
        btn_normal.clicked.connect(lambda: self.choisir("normal"))
        layout.addWidget(btn_normal)

        btn_difficile = QPushButton("🔥 Difficile\n(Avion toutes les 3s)")
        btn_difficile.setStyleSheet("padding: 12px; font-size: 14px;")
        btn_difficile.clicked.connect(lambda: self.choisir("difficile"))
        layout.addWidget(btn_difficile)

        btn_impossible = QPushButton("💀 IMPOSSIBLE\n(Avion toutes les 1.5s)")
        btn_impossible.setStyleSheet("padding: 12px; font-size: 14px; background-color: #8B0000; color: white;")
        btn_impossible.clicked.connect(lambda: self.choisir("impossible"))
        layout.addWidget(btn_impossible)

        self.setLayout(layout)

    def choisir(self, difficulte):
        self.difficulte_choisie = difficulte
        self.accept()


class FenetreFinJeu(QDialog):
    def __init__(self, victoire=True, temps=0, poses=0, crashes=0):
        super().__init__()
        self.setWindowTitle("Fin de partie")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        if victoire:
            # VICTOIRE
            titre = QLabel("🎉 VICTOIRE ! 🎉")
            titre.setStyleSheet("font-size: 24px; font-weight: bold; color: green; margin: 20px;")
            titre.setAlignment(Qt.AlignCenter)
            layout.addWidget(titre)

            minutes = temps // 60
            secondes = temps % 60

            stats = QLabel(f"Temps : {minutes:02d}:{secondes:02d}\n\n"
                           f"✅ Avions posés : {poses}\n"
                           f"💥 Avions crashés : {crashes}")
            stats.setStyleSheet("font-size: 16px; margin: 20px;")
            stats.setAlignment(Qt.AlignCenter)
            layout.addWidget(stats)
        else:
            # DÉFAITE
            titre = QLabel("💥 GAME OVER 💥")
            titre.setStyleSheet("font-size: 24px; font-weight: bold; color: red; margin: 20px;")
            titre.setAlignment(Qt.AlignCenter)
            layout.addWidget(titre)

            message = QLabel(f"3 crashs, vous avez perdu !\n\n"
                             f"Avions posés : {poses}\n"
                             f"Avions crashés : {crashes}")
            message.setStyleSheet("font-size: 16px; margin: 20px;")
            message.setAlignment(Qt.AlignCenter)
            layout.addWidget(message)

        # Boutons
        btn_recommencer = QPushButton("🔄 Recommencer")
        btn_recommencer.setStyleSheet("padding: 12px; font-size: 14px;")
        btn_recommencer.clicked.connect(lambda: self.done(1))  # Code 1 = recommencer
        layout.addWidget(btn_recommencer)

        btn_quitter = QPushButton("❌ Quitter")
        btn_quitter.setStyleSheet("padding: 12px; font-size: 14px;")
        btn_quitter.clicked.connect(lambda: self.done(0))  # Code 0 = quitter
        layout.addWidget(btn_quitter)

        self.setLayout(layout)


class MainWindow(BaseClass, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # === DIFFICULTÉ ===
        self.difficulte = "normal"
        self.spawn_intervals = {
            "facile": 8000,
            "normal": 5000,
            "difficile": 3000,
            "impossible": 1500
        }

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

        # === COMPTEURS ===
        self.avions_poses = 0
        self.avions_crashes = 0

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
        self.spawn_timer.start(self.spawn_intervals[self.difficulte])

        # === TIMER DE NIVEAU ===
        self.temps_ecoule = 0
        self.duree_jeu = 180  # 3 minutes (180 secondes)
        self.niveau_timer = QTimer()
        self.niveau_timer.timeout.connect(self.update_niveau)
        self.niveau_timer.start(1000)

        # === PAUSE ===
        self.en_pause = False

        # focus clavier
        self.setFocusPolicy(Qt.StrongFocus)

        # === SÉLECTION SOURIS ===
        self.scene.selectionChanged.connect(self.selection_changed)

        # === CONNEXIONS BOUTONS ===
        if hasattr(self, "btnRecommencer"):
            self.btnRecommencer.clicked.connect(self.recommencer)

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

        if hasattr(self, "pause"):
            self.pause.clicked.connect(self.pause_toggle)
            self.pause.setText("Pause")

        if hasattr(self, "btnQuitter"):
            self.btnQuitter.clicked.connect(self.quitter_relay)
        elif hasattr(self, "quitter"):
            self.quitter.clicked.connect(self.quitter_relay)

        # Afficher les stats initiales
        self.afficher_stats()

    # QUITTER
    def quitter_relay(self):
        self.close()

    # SPAWN AVION
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

    # UPDATE
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

            if not hasattr(avion, "icone_affichee") or avion.icone_affichee != avion.icone:
                pix = QPixmap(avion.icone)
                if pix.isNull():
                    pix = self.base_pixmap
                item.setPixmap(pix.scaled(60, 60))
                avion.icone_affichee = avion.icone

            if avion.etat in ["crash", "atterri"]:
                avions_a_supprimer.append(avion)
                items_a_supprimer.append(item)

        # Suppression et comptage
        for avion, item in zip(avions_a_supprimer, items_a_supprimer):
            # Compter avant de supprimer
            if avion.etat == "atterri":
                self.avions_poses += 1
                print(f"✅ Avion {avion.id} atterri ! Total : {self.avions_poses}")
            elif avion.etat == "crash":
                self.avions_crashes += 1
                print(f"💥 Avion {avion.id} crashé ! Total : {self.avions_crashes}")

                # Vérifier si 3 crashs = défaite
                if self.avions_crashes >= 6:
                    self.fin_jeu(victoire=False)
                    return

            self.avions.remove(avion)
            self.plane_items.remove(item)
            self.scene.removeItem(item)

            if self.avion_en_cours == avion:
                self.avion_en_cours = None

        fin_du_jeu = verifier_toutes_les_collisions(self.avions)
        if fin_du_jeu:
            print("FIN DE PARTIE - COLLISION")
            self.avions_crashes += 1
            if self.avions_crashes >= 3:
                self.fin_jeu(victoire=False)
                return

        self.afficher_infos_avion()
        self.afficher_stats()

    # SÉLECTION SOURIS
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

    # AFFICHAGE INFOS AVION
    def afficher_infos_avion(self):
        if not self.avion_en_cours:
            if hasattr(self, "altitude"):
                self.altitude.setText("—")
                self.carburant.setText("—")
                self.vitesse.setText("—")
            if hasattr(self, "jaugeCarburant"):
                self.jaugeCarburant.setValue(0)
            return

        a = self.avion_en_cours

        if hasattr(self, "altitude"):
            self.altitude.setText(f"{int(a.altitude)} m")
            self.carburant.setText(f"{int(a.carburant)} %")
            self.vitesse.setText(f"{int(a.vitesse)} km/h")

        if hasattr(self, "jaugeCarburant"):
            self.jaugeCarburant.setValue(int(a.carburant))

            if a.carburant < 20:
                self.jaugeCarburant.setStyleSheet("QProgressBar::chunk { background-color: red; }")
            elif a.carburant < 50:
                self.jaugeCarburant.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
            else:
                self.jaugeCarburant.setStyleSheet("QProgressBar::chunk { background-color: green; }")


    # AFFICHAGE STATS

    def afficher_stats(self):
        """Affiche les statistiques de jeu"""
        if hasattr(self, "labelPoses"):
            self.labelPoses.setText(f"{self.avions_poses}")
        if hasattr(self, "labelCrashes"):
            self.labelCrashes.setText(f"{self.avions_crashes}")


    # FIN DE JEU

    def fin_jeu(self, victoire=True):
        """Affiche la fenêtre de fin de jeu"""
        # Arrêter tous les timers
        self.timer.stop()
        self.spawn_timer.stop()
        self.niveau_timer.stop()

        # Afficher la fenêtre de fin
        fenetre = FenetreFinJeu(
            victoire=victoire,
            temps=self.temps_ecoule,
            poses=self.avions_poses,
            crashes=self.avions_crashes
        )

        resultat = fenetre.exec()

        if resultat == 1:  # Recommencer
            self.recommencer()
            # Redemander la difficulté
            menu = MenuDemarrage()
            if menu.exec() == QDialog.Accepted:
                self.changer_difficulte(menu.difficulte_choisie)
        else:  # Quitter
            self.close()
    # DIFFICULTÉ

    def changer_difficulte(self, niveau):
        """Change la difficulté du jeu"""
        self.difficulte = niveau
        interval = self.spawn_intervals[niveau]

        self.spawn_timer.stop()
        if not self.en_pause:
            self.spawn_timer.start(interval)

        print(f"🎮 Difficulté : {niveau.upper()} (spawn toutes les {interval / 1000}s)")

        if hasattr(self, "labelDifficulte"):
            self.labelDifficulte.setText(f"Difficulté : {niveau.capitalize()}")


    # RELAYS AVIONS

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

    # PAUSE / REPRENDRE
    def pause_toggle(self):
        if not self.en_pause:
            self.en_pause = True
            self.timer.stop()
            self.spawn_timer.stop()
            self.niveau_timer.stop()
            if hasattr(self, "pause"):
                self.pause.setText("Reprendre")
            print("JEU EN PAUSE")
        else:
            self.en_pause = False
            self.last_time = time.time()
            self.timer.start(30)
            self.spawn_timer.start(self.spawn_intervals[self.difficulte])
            self.niveau_timer.start(1000)
            if hasattr(self, "pause"):
                self.pause.setText("Pause")
            print("JEU REPRIS")


    # RECOMMENCER
    def recommencer(self):
        """Remet le jeu à zéro"""
        self.timer.stop()
        self.spawn_timer.stop()
        self.niveau_timer.stop()

        for item in self.plane_items:
            self.scene.removeItem(item)

        self.avions.clear()
        self.plane_items.clear()
        self.avion_en_cours = None
        self.afficher_infos_avion()
        self.next_id = 0

        # Réinitialiser les compteurs
        self.avions_poses = 0
        self.avions_crashes = 0
        self.afficher_stats()

        self.temps_ecoule = 0
        if hasattr(self, "timerNiveau"):
            self.timerNiveau.setText("00:00")

        self.en_pause = False
        if hasattr(self, "pause"):
            self.pause.setText("Pause")

        self.last_time = time.time()
        self.timer.start(30)
        self.spawn_timer.start(self.spawn_intervals[self.difficulte])
        self.niveau_timer.start(1000)

        print("🔄 JEU REDÉMARRÉ")

    # UPDATE NIVEAU
    def update_niveau(self):
        """Met à jour le timer de niveau"""
        if self.en_pause:
            return

        self.temps_ecoule += 1

        minutes = self.temps_ecoule // 60
        secondes = self.temps_ecoule % 60

        if hasattr(self, "timerNiveau"):
            self.timerNiveau.setText(f"{minutes:02d}:{secondes:02d}")

        # Vérifier si victoire (temps écoulé)
        if self.temps_ecoule >= self.duree_jeu:
            self.fin_jeu(victoire=True)


def main():
    app = QApplication(sys.argv)

    # Afficher le menu de démarrage
    menu = MenuDemarrage()
    if menu.exec() == QDialog.Accepted:
        difficulte = menu.difficulte_choisie
        print(f"🎮 Difficulté choisie : {difficulte}")

        window = MainWindow()
        window.changer_difficulte(difficulte)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()