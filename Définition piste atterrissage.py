
class Piste:
    def __init__(self, altitude, position, longueur, cooldown):
        self.altitude = altitude
        self.position = position
        self.longueur = longueur
        self.disponibilite = False
        self.cooldown = cooldown

    def atterrir(self):
        return not self.disponibilite


    def



