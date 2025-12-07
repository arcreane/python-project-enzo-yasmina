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
        "noir": "assets/avions/avion_jet_noir.png"
    },
    "ligne": {
        "vert": "assets/avions/avion_ligne_vert.png",
        "orange": "assets/avions/avion_ligne_orange.png",
        "rouge": "assets/avions/avion_ligne_rouge.png",
        "noir": "assets/avions/avion_ligne_noir.png"
    },
    "cargo": {
        "vert": "assets/avions/avion_cargo_vert.png",
        "orange": "assets/avions/avion_cargo_orange.png",
        "rouge": "assets/avions/avion_cargo_rouge.png",
        "noir": "assets/avions/avion_cargo_noir.png"
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
        self.icone = ICONS_AVIONS[self.classe][self.couleur]

        self.altitude = altitude
        self.carburant = carburant

        self.vitesse = max(self.vitesse_min, min(vitesse, self.vitesse_max))
        self.cap = cap
        self.id = id
        self.position = position

        self.altitude_limitesup = altitude_limitesup
        self.altitude_limiteinf = altitude_limiteinf

        self.collisions = 0

        self.en_panne = False
        self.temps_panne = None
        self.vitesse_secours = self.vitesse * 0.4




    def monter(self):
        self.altitude = min(self.altitude + self.delta_montee, self.altitude_limitesup)

    def descendre(self):
        self.altitude = max(self.altitude - self.delta_descente, self.altitude_limiteinf)

    def accelerer(self):
        self.vitesse = min(self.vitesse + 20, self.vitesse_max)

    def decelerer(self):
        self.vitesse = max(self.vitesse - 20, self.vitesse_min)

    def mettre_en_attente(self):
        self.etat = "en attente"
        self.vitesse = 0
        print(f"⏸ Avion {self.id} en attente")

    def reprendre_vol(self):
        self.etat = "en vol"
        self.vitesse = self.vitesse_min
        print(f"▶ Avion {self.id} reprend le vol")

    def atterrir(self):
        self.etat = "atterri"
        self.vitesse = 0
        print(f"🛬 Avion {self.id} est sur le point d'atterrir")




    def gerer_bordures(self):
        x, y = self.position
        taille = 30

        if x < X_MIN + taille or x > X_MAX - taille:
            self.cap = 180 - self.cap

        if y < Y_MIN + taille or y > Y_MAX - taille:
            self.cap = -self.cap

        self.cap %= 360
        self.position = (x, y)


    def update_position(self, dt):

        if self.etat in ["crash", "atterri", "en attente"]:
            return



        self.carburant -= dt * 0.8


        if self.carburant <= 15 and not self.en_panne:
            self.declencher_panne()

        if self.en_panne:
            self.vitesse = self.vitesse_secours

            if time.time() - self.temps_panne > 10:
                self.couleur = "noir"
                self.icone = ICONS_AVIONS[self.classe]["noir"]
                self.etat = "crash"
                print(f"Avion {self.id} détruit")
                return


        COEFF_VITESSE = 0.15
        dx = self.vitesse * COEFF_VITESSE * math.cos(math.radians(self.cap)) * dt
        dy = self.vitesse * COEFF_VITESSE * math.sin(math.radians(self.cap)) * dt

        x, y = self.position
        self.position = (x + dx, y + dy)

        self.gerer_bordures()


    def declencher_panne(self):
        self.en_panne = True
        self.temps_panne = time.time()
        self.couleur = "rouge"
        self.icone = ICONS_AVIONS[self.classe]["rouge"]
        print(f"PANNE MOTEUR Avion {self.id}")




    def verifier_collision(self, autre, distance_min=50):

        if self is autre:
            return False

        if self.etat == "crash" or autre.etat == "crash":
            return False

        x1, y1 = self.position
        x2, y2 = autre.position

        if math.hypot(x2 - x1, y2 - y1) < distance_min:
            print(f"COLLISION {self.id} <-> {autre.id}")
            self.etat = "crash"
            autre.etat = "crash"

            self.couleur = "noir"
            autre.couleur = "noir"

            self.icone = ICONS_AVIONS[self.classe]["noir"]
            autre.icone = ICONS_AVIONS[autre.classe]["noir"]

            return True

        return False


def verifier_toutes_les_collisions(liste_avions):
    global collisions_globales

    for i in range(len(liste_avions)):
        for j in range(i + 1, len(liste_avions)):
            if liste_avions[i].verifier_collision(liste_avions[j]):
                collisions_globales += 1
                print(f"COLLISIONS : {collisions_globales}/{MAX_COLLISIONS}")

                if collisions_globales >= MAX_COLLISIONS:
                    print("FIN DE PARTIE")
                    return True

    return False
