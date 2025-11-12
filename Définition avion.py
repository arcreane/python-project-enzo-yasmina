class Avion:
    def __init__(self, etat, altitude, carburant, vitesse, couleur, id, position, classe = "inconnu", altitude_limitesup, altitude_limiteinf):
        self.altitude = altitude # en m
        self.carburant = carburant # en %
        self.vitesse = vitesse # en km/h
        self.couleur = couleur
        self.id = id
        self.position = position # définie par (x,y)
        self.classe = classe #jet, ligne, cargo...
        self.etat = "en vol" #par défaut
        self.altitude_limitesup = 3000 #à ajuster
        self.altitude_limiteinf = 1000 #à ajuster

    def monter(self, delta = 1000 ):    #delta (en m) à ajuster plus tard
        self.altitude += delta
        if self.altitude >= self.altitude_limitesup:
            self.altitude = self.altitude_limitesup
            print(f"Altitude : {self.altitude} m. Attention à la limite d'altitude de jeu !")
        else:
            print(f"Altitude : {self.altitude} m")



    def descendre(self, delta = 1000 ):     #delta (en m) à ajuster plus tard
        self.altitude -= delta
        if  self.altitude =< self.altitude_limiteinf:
            self.altitude = self.altitudeinf
            print(f"Altitude : {self.altitude} m. Attention à la limite d'altitude de jeu!")
        else:
            print(f"Altitude : {self.altitude} m")




