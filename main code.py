from Avion import Avion
from Piste import Piste

avion1 = Avion(
    altitude=500,
    carburant=80,
    vitesse=50,
    cap=90,
    couleur="bleu",
    id="A320",
    position=(100, 200),
    altitude_limitesup=10000,
    altitude_limiteinf=0
)

piste1 = Piste(position=(100, 200), longueur=300)

print("Atterrissage :", piste1.atterrir(avion1))
print("État avion :", avion1.etat)
print("Position avion :", avion1.position)
print("Altitude avion :", avion1.altitude)
