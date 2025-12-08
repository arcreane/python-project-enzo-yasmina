import random
import math
from avion import Avion
from Bordures import X_MIN, X_MAX, Y_MIN, Y_MAX

class GestionAvions:
    def __init__(self):
        self.avions = []
        self.collisions_globales = 0
        self.partie_terminee = False

    def spawn_avion(self):
        # 1) Spawn aléatoire sur un bord
        bord = random.choice(["haut", "bas", "gauche", "droite"])

        if bord == "haut":
            x = random.uniform(X_MIN, X_MAX)
            y = Y_MAX
            cap = random.uniform(200, 340)  # vers le bas
        elif bord == "bas":
            x = random.uniform(X_MIN, X_MAX)
            y = Y_MIN
            cap = random.uniform(20, 160)  # vers le haut
        elif bord == "gauche":
            x = X_MIN
            y = random.uniform(Y_MIN, Y_MAX)
            cap = random.uniform(-70, 70)  # vers la droite
        else:  # droite
            x = X_MAX
            y = random.uniform(Y_MIN, Y_MAX)
            cap = random.uniform(110, 250)  # vers la gauche

        # 2) Paramètres aléatoires
        altitude = random.randint(5000, 12000)
        carburant = random.uniform(40, 100)
        vitesse = random.uniform(50, 83.33)
        couleur = random.choice(["rouge", "vert", "bleu", "jaune"])
        altitude_sup = 15000
        altitude_inf = 2000
        id = f"A{len(self.avions)+1}"

        avion = Avion(
            altitude=altitude,
            carburant=carburant,
            vitesse=vitesse,
            cap=cap,
            couleur=couleur,
            id=id,
            position=(x, y),
            altitude_limitesup=altitude_sup,
            altitude_limiteinf=altitude_inf
        )

        self.avions.append(avion)
        print(f"Nouvel avion généré : {id} (cap={cap:.1f}°, vitesse={vitesse:.1f} m/s)")

    def update(self, dt):
        if self.partie_terminee:
            return

        # mise à jour des positions
        for avion in self.avions:
            avion.update_position(dt)
            avion.consommer_carburant(dt)

        # vérifier collisions
        for i in range(len(self.avions)):
            for j in range(i+1, len(self.avions)):
                a1 = self.avions[i]
                a2 = self.avions[j]
                if a1.verifier_collision(a2, distance_min=20):
                    self.collisions_globales += 1
                    print(f" Collision détectée ! Total = {self.collisions_globales}")

                    if self.collisions_globales >= 3:
                        self.partie_terminee = True
                        print(" Partie terminée après 3 collisions.")
                        return
