import time
from avion_spawn_random import generer_avion_collision
from Avion import verifier_toutes_les_collisions

NB_AVIONS = 5
TICK = 0.03
DUREE_JEU = 30 #secondes

avions = []
for i in range(NB_AVIONS):
    avions.append(generer_avion_collision())

print("Jeu lancé")
print(f"{NB_AVIONS} avions en vol")

temps_depart = time.time()
temps_precedent = time.time()

while True:
    maintenant = time.time()
    dt = maintenant - temps_precedent
    temps_precedent = maintenant

    for avion in avions:
        avion.update_position(dt)

    fin = verifier_toutes_les_collisions(avions)
    if fin:
        print("Arrêt du jeu (collisions)")
        break

    if maintenant - temps_depart > DUREE_JEU:
        print("TEMPS ÉCOULÉ - FIN DU JEU")
        break

    time.sleep(TICK)
