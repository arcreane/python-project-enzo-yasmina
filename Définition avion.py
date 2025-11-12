class Avion:
    def __init__(self, altitude, carburant, vitesse, couleur, id, position, altitude_limitesup, altitude_limiteinf, classe = "inconnu", etat = "en vol"):
        self.altitude = altitude # en m
        self.carburant = carburant # en %
        self.vitesse = vitesse # en km/h
        self.couleur = couleur
        self.id = id
        self.position = position # définie par (x,y)
        self.classe = classe #jet, ligne, cargo...
        self.etat = etat
        self.altitude_limitesup = altitude_limitesup #à ajuster
        self.altitude_limiteinf = altitude_limiteinf#à ajuster

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


    from Bordures import X_MIN, X_MAX, Y_MIN, Y_MAX










