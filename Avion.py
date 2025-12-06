import math
from Bordures import X_MIN, X_MAX, Y_MIN, Y_MAX
MAX_COLLISIONS = 3
collisions_globales = 0


class Avion:
    def __init__(self, altitude, carburant, vitesse, cap, couleur, id, position, altitude_limitesup, altitude_limiteinf, classe = "inconnu", etat = "en vol"):
        self.altitude = altitude # en m
        self.carburant = carburant # en %
        self.vitesse = vitesse # en m/s
        self.couleur = couleur
        self.cap = cap
        self.id = id
        self.position = position # définie par (x,y)
        self.classe = classe #jet, ligne, cargo...
        self.etat = etat
        self.altitude_limitesup = altitude_limitesup #à ajuster
        self.altitude_limiteinf = altitude_limiteinf#à ajuster
        self.collisions = 0

    def monter(self, delta = 1000 ):    #delta (en m) à ajuster plus tard
        self.altitude += delta
        if self.altitude >= self.altitude_limitesup:
            self.altitude = self.altitude_limitesup
            print(f"Altitude : {self.altitude} m. Attention à la limite d'altitude de jeu !")
        else:
            print(f"Altitude : {self.altitude} m")


    def descendre(self, delta = 1000 ):     #delta (en m) à ajuster plus tard
        self.altitude -= delta
        if  self.altitude <= self.altitude_limiteinf:
            self.altitude = self.altitude_limiteinf
            print(f"Altitude : {self.altitude} m. Attention à la limite d'altitude de jeu!")
        else:
            print(f"Altitude : {self.altitude} m")

    def mettre_en_attente(self):
        self.etat = "en attente"
        self.vitesse = 0
        print(f"Mise en attente : {self.id}")

    def reprendre_vol(self,vitesse):
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
            dy = self.vitesse * math.sin(math.radians(self.cap)) * dt       #dt en s et vitesse en m/s

            x, y = self.position
            x += dx
            y += dy
            self.position = (x, y)
            self.gerer_bordures()

    def accelerer(self,delta = 7, vitesse_max = 300):
        if self.etat == "en attente" :
            print("Impossible d'accélérer : avion en attente.")
            return

        self.vitesse += delta
        if self.vitesse > vitesse_max:
            self.vitesse = vitesse_max
            print(f"Vitesse maximale atteinte : {self.vitesse:.1f} m/s")
        else:
            print(f"Nouvelle vitesse : {self.vitesse:.1f} m/s")


    def decelerer(self, delta=7, vitesse_min=0):
        if self.etat == "en attente" :
            print("Impossible de décélérer : avion en attente.")
            return

        self.vitesse -= delta
        if self.vitesse < vitesse_min:
            self.vitesse = vitesse_min
            print(f"Vitesse minimale atteinte : {self.vitesse:.1f} m/s")
        else:
            print(f"Nouvelle vitesse : {self.vitesse:.1f} m/s")

    def vitesse_kmh(self):
        return self.vitesse*3.6

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
            self.etat = "crash"
            autre_avion.etat = "crash"
            return True

        return False


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


def infos(self):
    return {"id": self.id,
            "position": self.position,
            "vitesse": self.vitesse,
            "altitude": self.altitude,
            "classe" : self.classe,
            "etat" : self.etat}



     

