import math
import time

# ✅ Limites DIRECTES de la scène (plus de Bordures.py)
X_MIN = 0
X_MAX = 832
Y_MIN = 0
Y_MAX = 480

MAX_COLLISIONS = 3
collisions_globales = 0

avion_en_approche = None  # ✅ UN SEUL AVION AUTORISÉ À ATTERRIR

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

        self.en_panne = False
        self.temps_panne = None
        self.vitesse_secours = self.vitesse * 0.4

        self.point_piste = (416, 240)

    # -------------------------
    # COMMANDES
    # -------------------------
    def monter(self):
        self.altitude = min(self.altitude + self.delta_montee, self.altitude_limitesup)

    def descendre(self):
        self.altitude = max(self.altitude - self.delta_descente, self.altitude_limiteinf)

    def accelerer(self):
        self.vitesse = min(self.vitesse + 50, self.vitesse_max)

    def decelerer(self):
        self.vitesse = max(self.vitesse - 50, self.vitesse_min)

    def atterrir(self):
        global avion_en_approche

        if self.etat == "en vol" and avion_en_approche is None:
            self.etat = "atterrissage"
            avion_en_approche = self
            print(f"🛬 Avion {self.id} autorisé à atterrir")

    # -------------------------
    # BORDURES ✅ CORRIGÉES
    # -------------------------
    def gerer_bordures(self):
        x, y = self.position
        taille = 30

        if x < X_MIN + taille:
            x = X_MIN + taille
            self.cap = 180 - self.cap

        elif x > X_MAX - taille:
            x = X_MAX - taille
            self.cap = 180 - self.cap

        if y < Y_MIN + taille:
            y = Y_MIN + taille
            self.cap = -self.cap

        elif y > Y_MAX - taille:
            y = Y_MAX - taille
            self.cap = -self.cap

        self.cap %= 360
        self.position = (x, y)

    # -------------------------
    # MOUVEMENT
    # -------------------------
    def update_position(self, dt):
        global avion_en_approche

        if self.etat in ["crash", "atterri"]:
            return

        # ✅ PHASE ATTERRISSAGE
        if self.etat == "atterrissage":
            xp, yp = self.point_piste
            x, y = self.position

            self.cap = math.degrees(math.atan2(yp - y, xp - x))
            self.vitesse = max(30, self.vitesse - 80 * dt)
            self.altitude = max(0, self.altitude - 700 * dt)

            dx = self.vitesse * 0.15 * math.cos(math.radians(self.cap)) * dt
            dy = self.vitesse * 0.15 * math.sin(math.radians(self.cap)) * dt

            self.position = (x + dx, y + dy)

            if math.hypot(xp - x, yp - y) < 15 and self.altitude <= 3:
                self.etat = "atterri"
                self.vitesse = 0
                self.altitude = 0
                avion_en_approche = None
                print(f"✅ Avion {self.id} a atterri")

            return

        # ✅ CONSOMMATION
        self.carburant -= dt * 0.8

        if self.carburant <= 15 and not self.en_panne:
            self.declencher_panne()

        if self.en_panne:
            self.vitesse = self.vitesse_secours
            if time.time() - self.temps_panne > 10:
                self.etat = "crash"
                self.couleur = "noir"
                self.icone = ICONS_AVIONS[self.classe]["noir"]
                print(f"💥 Avion {self.id} détruit")
                return

        dx = self.vitesse * 0.15 * math.cos(math.radians(self.cap)) * dt
        dy = self.vitesse * 0.15 * math.sin(math.radians(self.cap)) * dt

        x, y = self.position
        self.position = (x + dx, y + dy)

        self.gerer_bordures()

    # -------------------------
    # PANNE
    # -------------------------
    def declencher_panne(self):
        self.en_panne = True
        self.temps_panne = time.time()
        self.couleur = "rouge"
        self.icone = ICONS_AVIONS[self.classe]["rouge"]

    # -------------------------
    # COLLISION
    # -------------------------
    def verifier_collision(self, autre):

        if self.etat in ["crash", "atterri", "atterrissage"]:
            return False
        if autre.etat in ["crash", "atterri", "atterrissage"]:
            return False

        if abs(self.altitude - autre.altitude) > 300:
            return False

        x1, y1 = self.position
        x2, y2 = autre.position

        if math.hypot(x2 - x1, y2 - y1) < 50:
            self.etat = autre.etat = "crash"
            self.couleur = autre.couleur = "noir"
            print(f"💥 COLLISION {self.id} <-> {autre.id}")
            return True

        return False


# -------------------------
# COLLISIONS GLOBALES
# -------------------------
def verifier_toutes_les_collisions(liste_avions):
    global collisions_globales

    for i in range(len(liste_avions)):
        for j in range(i + 1, len(liste_avions)):
            if liste_avions[i].verifier_collision(liste_avions[j]):
                collisions_globales += 1
                if collisions_globales >= MAX_COLLISIONS:
                    return True

    return False
