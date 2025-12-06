import math
from Bordures import X_MIN, X_MAX, Y_MIN, Y_MAX

MAX_COLLISIONS = 3
collisions_globales = 0

CLASSES_AVIONS = {
    "jet": {
        "vmin": 180,
        "vmax": 300,
        "montee": 1200,
        "descente": 1200,
        "couleur": "bleu"
    },
    "ligne": {
        "vmin": 140,
        "vmax": 260,
        "montee": 900,
        "descente": 900,
        "couleur": "vert"
    },
    "cargo": {
        "vmin": 100,
        "vmax": 200,
        "montee": 700,
        "descente": 700,
        "couleur": "orange"
    }}

ICONS_AVIONS = {
    "jet": {
        "vert": "assets/avions/avion_cessna_vert.png",
        "orange": "assets/avions/avion_cessna_orange.png",
        "rouge": "assets/avions/avion_cessna_rouge.png",
        "noir": "assets/avions/avion_cessna_noir.png",
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
        "noir": "assets/avions/avion_cargo_noir.png",}}



class Avion:
    def __init__(self, altitude, carburant, vitesse, cap, id, position,
                 altitude_limitesup, altitude_limiteinf, classe="ligne", etat="en vol"):

        self.classe = classe
        self.etat = etat

        data = CLASSES_AVIONS[classe]
        self.vitesse_min = data["vmin"]
        self.vitesse_max = data["vmax"]
        self.delta_montee = data["montee"]
        self.delta_descente = data["descente"]
        self.couleur = data["couleur"]

        self.altitude = altitude
        self.carburant = carburant
        self.vitesse = max(self.vitesse_min, min(vitesse, self.vitesse_max))
        self.cap = cap
        self.id = id
        self.position = position
        self.altitude_limitesup = altitude_limitesup
        self.altitude_limiteinf = altitude_limiteinf
        self.collisions = 0
        self.icone = ICONS_AVIONS[self.classe][self.couleur]


    def monter(self):
        self.altitude += self.delta_montee
        if self.altitude >= self.altitude_limitesup:
            self.altitude = self.altitude_limitesup

    def descendre(self):
        self.altitude -= self.delta_descente
        if self.altitude <= self.altitude_limiteinf:
            self.altitude = self.altitude_limiteinf

    def mettre_en_attente(self):
        self.etat = "en attente"
        self.vitesse = 0
        print(f"Mise en attente : {self.id}")

    def reprendre_vol(self, vitesse):
        self.etat = "en vol"
        self.vitesse = vitesse
        print(f"Mise en vol : {self.id}")

    def urgence(self):
        self.etat = "en urgence"
        print(f"{self.id} doit atterir en urgence")

    def gerer_bordures(self):
        x, y = self.position

        if x <= X_MIN + 10 or x >= X_MAX - 10:
            self.cap = 100 - self.cap

        if y <= Y_MIN + 10 or y >= Y_MAX - 10:
            self.cap = -self.cap

        self.cap %= 360

    def update_position(self, dt):
        if self.etat != "en attente":
            dx = self.vitesse * math.cos(math.radians(self.cap)) * dt
            dy = self.vitesse * math.sin(math.radians(self.cap)) * dt

            x, y = self.position
            x += dx
            y += dy
            self.position = (x, y)
            self.gerer_bordures()

    def accelerer(self, delta=10):
        if self.etat == "en attente":
            return
        self.vitesse += delta
        if self.vitesse > self.vitesse_max:
            self.vitesse = self.vitesse_max

    def decelerer(self, delta=10):
        if self.etat == "en attente":
            return
        self.vitesse -= delta
        if self.vitesse < self.vitesse_min:
            self.vitesse = self.vitesse_min

    def vitesse_kmh(self):
        return self.vitesse * 3.6

    def changer_cap(self, delta_cap):
        self.cap = (self.cap + delta_cap) % 360
        print(f"Cap actuel : {self.cap}°")

    def verifier_collision(self, autre_avion, distance_min=50):
        if self is autre_avion:
            return False

        if self.etat == "crash" or autre_avion.etat == "crash":
            return False

        x1, y1 = self.position
        x2, y2 = autre_avion.position
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        if distance < distance_min:
            print(f"COLLISION entre Avion {self.id} et Avion {autre_avion.id}")
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

    def infos(self):
        return {
            "id": self.id,
            "position": self.position,
            "vitesse": self.vitesse,
            "altitude": self.altitude,
            "classe": self.classe,
            "etat": self.etat
        }

    def est_pose(self):
        return self.etat == "posé"

    def get_icon_path(self):
        return f"assets/avions/avion_{self.classe}"


def verifier_toutes_les_collisions(liste_avions):
    global collisions_globales

    for i in range(len(liste_avions)):
        for j in range(i + 1, len(liste_avions)):
            avion1 = liste_avions[i]
            avion2 = liste_avions[j]

            if avion1.verifier_collision(avion2):
                collisions_globales += 1
                print(f"COLLISIONS TOTALES : {collisions_globales}/{MAX_COLLISIONS}")

                if collisions_globales >= MAX_COLLISIONS:
                    print("3 COLLISIONS ATTEINTES = FIN DE PARTIE")
                    return True

    return False
