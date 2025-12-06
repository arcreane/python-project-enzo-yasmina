from collections import deque
import math as m

class Aeroport:
    def __init__(self, zone_position, rayon_zone = 80):
        self.zone_position = zone_position
        self.rayon_zone = rayon_zone
        self.piste_occupee = False
        self.avion_en_approche = None
        self.file_attente = deque()
        self.file_urgence = deque()


    def detecter_zone(self, avion):
        x1, y1 = avion.position
        x2, y2 = self.zone_position
        distance = m.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        return distance <= self.rayon_zone

    def demander_atterrissage(self, avion):
        if avion.etat == "en urgence":
            print(f"URGENCE PRIORITAIRE : Avion {avion.id}")
            self.file_urgence.append(avion)

        else:
            print(f"Avion {avion.id} mis en attente")
            self.file_attente.append(avion)
            avion.mettre_en_attente()

    def gerer_piste(self):
        if self.piste_occupee:
            return

        if len(self.file_urgence) > 0:
            avion = self.file_urgence.popleft()

        elif len(self.file_attente) > 0:
            avion = self.file_attente.popleft()

        else:
            return

        self.avion_en_approche = avion
        self.piste_occupee = True
        avion.reprendre_vol(avion.vitesse)
        print(f"Avion {avion.id} autorisé à atterrir")


    def finaliser_atterrissage(self):
        if self.avion_en_approche:
            print(f"Avion {self.avion_en_approche.id} a atterri")
            self.avion_en_approche.etat = "posé"
            self.avion_en_approche.vitesse = 0
            self.avion_en_approche = None
            self.piste_occupee = False

