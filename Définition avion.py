class Avion:
    def __init__(self, etat, altitude, carburant, vitesse, couleur, id, position, classe = "inconnu"):
        self.altitude = altitude # en m
        self.carburant = carburant # en %
        self.vitesse = vitesse # en km/h
        self.couleur = couleur
        self.id = id
        self.position = position # définie par (x,y)
        self.classe = classe #jet, ligne, cargo...



