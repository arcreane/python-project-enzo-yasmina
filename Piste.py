import time
import math

class Piste:
    def __init__(self, position, longueur, altitude_piste=0, cooldown=10):
        self.altitude_piste = altitude_piste
        self.position = position
        self.longueur = longueur
        self.disponibilite = True
        self.cooldown = cooldown
        self.dernier_atterrissage = 0

    def can_land(self):
        if self.dernier_atterrissage == 0:
            return True

        temps_ecoule = time.time() - self.dernier_atterrissage

        if temps_ecoule >= self.cooldown:
            self.disponibilite = True

        return self.disponibilite

    def atterrir(self, avion):
        if not self.can_land():
            return False

        if avion.altitude > self.altitude_piste:
            return False

        ax, ay = avion.position
        px, py = self.position

        distance = math.sqrt((px - ax)**2 + (py - ay)**2)
        if distance > self.longueur:
            return False

        avion.etat = "au sol"
        avion.position = self.position
        avion.altitude = self.altitude_piste

        self.disponibilite = False
        self.dernier_atterrissage = time.time()

        return True
