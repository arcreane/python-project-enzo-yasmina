import math
import time
from Bordures import X_MIN, X_MAX, Y_MIN, Y_MAX

MAX_COLLISIONS = 3
collisions_globales = 0

CLASSES_AVIONS = {
    "jet": {"vmin": 180, "vmax": 300, "montee": 1200, "descente": 1200},
    "ligne": {"vmin": 140, "vmax": 260, "montee": 900, "descente": 900},
    "cargo": {"vmin": 100, "vmax": 200, "montee": 700, "descente": 700}
}

ICONS_AVIONS = {
    "jet": {
        "vert": "assets/avions/avion_jet_vert.png",
        "orange": "assets/avions/avion_jet_orange.png",
        "rouge": "assets/avions/avion_jet_rouge.png",
        "noir": "assets/avions/avion_jet_noir.png",
    },
    "ligne": {
        "vert": "assets/avions/avion_ligne_vert.png",
        "orange": "assets/avions/avion_ligne_orange.png",
        "rouge": "assets/avions/avion_ligne_rouge.png",
        "noir": "assets/avions/avion_ligne_noir.png",
    },
    "cargo": {
        "vert": "assets/avions/avion_cargo_vert.png",
        "orange": "assets/avions/avion_cargo_orange.png",
        "rouge": "assets/avions/avion_cargo_rouge.png",
        "noir": "assets/avions/avion_cargo_noir.png",
    }
}


class Avion:
    def __init__(self, altitude, carburant, vitesse, cap, id, position,
                 altitude_limitesup, altitude_limiteinf,
                 classe="ligne", couleur="vert", etat="en vol"):

        self.classe = classe
        self.etat = etat

        data = CLASSES_AVIONS[classe]
        self.vitesse_min = data["vmin"]
        self.vitesse_max = data["vmax"]
        self.delta_montee = data["montee"]
        self.delta_descente = data["descente"]

        self.couleur = couleur

        self.altitude = altitude
        self.carburant = carburant
        self.cap = cap
        self.id = id
        self.position = position
        self.altitude_limitesup = altitude_limitesup
        self.altitude_limiteinf = altitude_limiteinf

        self.vitesse = max(self.vitesse_min, min(vitesse, self.vitesse_max))
        self.vitesse_secours = self.vitesse * 0.4

        self.timer_panne = None
        self.collisions = 0

        self.icone = ICONS_AVIONS[self.classe][self.couleur]

    def gerer_bordures(self):
        x, y = self.position
        taille = 30

        if x < X_MIN + taille or x > X_MAX - taille:
            self.cap = 180 - self.cap

        if y < Y_MIN + taille or y > Y_MAX - taille:
            self.cap = -self.cap

        self.cap = self.cap % 360
        self.position = (x, y)

    def update_position(self, dt):
        if self.etat == "crash":
            return

        COEFF_VITESSE = 0.15

        dx = self.vitesse * COEFF_VITESSE * math.cos(math.radians(self.cap)) * dt
        dy = self.vitesse * COEFF_VITESSE * math.sin(math.radians(self.cap)) * dt

        x, y = self.position
        self.position = (x + dx, y + dy)

        self.gerer_bordures()


        self.carburant -= 0.02 * self.vitesse / 200


        if self.carburant < 20 and self.couleur == "vert":
            self.couleur = "orange"
            self.icone = ICONS_AVIONS[self.classe]["orange"]


        if self.carburant <= 0 and self.etat != "crash":
            if self.etat != "panne_moteur":
                self.etat = "panne_moteur"
                self.couleur = "rouge"
                self.icone = ICONS_AVIONS[self.classe]["rouge"]
                self.vitesse = self.vitesse_secours
                self.timer_panne = time.time()


        if self.etat == "panne_moteur":
            if time.time() - self.timer_panne > 10:
                self.etat = "crash"
                self.vitesse = 0
                self.couleur = "noir"
                self.icone = ICONS_AVIONS[self.classe]["noir"]

    def verifier_collision(self, autre_avion, distance_min=50):
        if self is autre_avion:
            return False

        if self.etat == "crash" or autre_avion.etat == "crash":
            return False

        x1, y1 = self.position
        x2, y2 = autre_avion.position
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        if distance < distance_min:
            self.collisions += 1
            autre_avion.collisions += 1

            self.couleur = "noir"
            autre_avion.couleur = "noir"

            self.icone = ICONS_AVIONS[self.classe]["noir"]
            autre_avion.icone = ICONS_AVIONS[autre_avion.classe]["noir"]

            self.etat = "crash"
            autre_avion.etat = "crash"
            return True

        return False


def verifier_toutes_les_collisions(liste_avions):
    global collisions_globales

    for i in range(len(liste_avions)):
        for j in range(i + 1, len(liste_avions)):
            if liste_avions[i].verifier_collision(liste_avions[j]):
                collisions_globales += 1
                print(f"COLLISIONS TOTALES : {collisions_globales}/{MAX_COLLISIONS}")
                if collisions_globales >= MAX_COLLISIONS:
                    print("FIN DE PARTIE")
                    return True
    return False
