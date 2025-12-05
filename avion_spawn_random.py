import random
import math as m
from Avion import Avion
from Bordures import X_MIN, Y_MIN, X_MAX, Y_MAX

ID_COMPTEUR = 0

zones_conflit = [(X_MAX*0.3, Y_MAX*0.5), (X_MAX*0.7, Y_MAX*0.5), (X_MAX*0.9, Y_MAX*0.5)]
altitudes_conflit = [6000, 7000 ,8000]
vitesses = [140 ,180, 240, 300]

def normal(vx, vy):
    norme = m.sqrt(vx**2 + vy**2)
    return vx/norme, vy/norme

def generer_avion_collision():
    global ID_COMPTEUR
    ID_COMPTEUR += 1
    bord = random.choice(["haut", "bas", "gauche", "droite"])

    if bord == "haut":
        x, y = random.uniform(X_MIN, X_MAX), Y_MAX

    elif bord == "bas":
        x, y = random.uniform(X_MIN, X_MAX), Y_MIN

    elif bord == "gauche":
        x, y = X_MIN, random.uniform(Y_MIN, Y_MAX)

    else:
        x, y = X_MAX, random.uniform(Y_MIN, Y_MAX)

    position = (x,y)
    cible_x, cible_y = random.choice(zones_conflit)
    dx = cible_x - x
    dy = cible_y - y
    ux, uy = normal(dx, dy)

    vitesse = random.choice(vitesses)
    vx = vitesse * ux
    vy = vitesse * uy

    cap = m.degrees(m.atan2(vy, vx))
    altitude = random.choice(altitudes_conflit)

    avion = Avion(altitude = altitude,
                  carburant = 100,
                  vitesse = vitesse,
                  cap = cap,
                  couleur = "rouge",
                  id = ID_COMPTEUR,
                  position = position,
                  altitude_limitesup = 9000,
                  altitude_limiteinf = 5000,
                  classe = "collision",
                  etat = "en vol")

    return avion





