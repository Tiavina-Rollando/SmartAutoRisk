import random
import csv

N = 2000


def calcul_variation(niveau_risque, type_vehicule, nombre_places, usage, tarif, valeur):

    if type_vehicule == 0:  # moto
        if valeur < 5000:
            base = 3 
        elif 5000 <= valeur < 15000:
            base = 5 
        else:            
            base = 7
    else:  # voiture
        if valeur <= 30000:
            base = 7 
        elif 30000 < valeur <= 70000:
            base = 10
        else:
            base = 15

    variation = base

    #nombre de places
    variation += nombre_places * base * 0.05 # augmenté de 5% de la base pour chaque place pour plus d’impact

    # impact risque
    variation += niveau_risque * base * 0.1 # augmenté de 10% de la base par niveau de risque

    # transport commercial
    if usage == 1:
        variation += base * 0.2 # augmenté de 20% de la valeur pour plus d’impact

    # assurance tout risque
    if tarif == 1:
        variation += base * 0.4 # augmenté de 40% de la valeur pour plus d’impact

    return round(variation, 2)


with open("../data/dataset_rate.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "niveau_risque",
        "type_vehicule",
        "nombre_places",
        "usage",
        "tarif",
        "valeur_vehicule",
        "variation_frais"
    ])

    for _ in range(N):

        niveau_risque = random.randint(0, 2)

        type_vehicule = random.randint(0, 1)  # 0 moto / 1 voiture

        if type_vehicule == 0:  # moto
            nombre_places = 2
        else:
            nombre_places = random.choice([2, 5, 7, 9, 12, 15, 22, 30])

        usage = random.randint(0, 1)

        tarif = random.randint(0, 1)

        if type_vehicule == 0:  # moto
            valeur = random.randint(1000, 50000)
        else:  # voiture
            valeur = random.randint(10000, 100000)

        variation = calcul_variation(
            niveau_risque,
            type_vehicule,
            nombre_places,
            usage,
            tarif,
            valeur
        )

        writer.writerow([
            niveau_risque,
            type_vehicule,
            nombre_places,
            usage,
            tarif,
            valeur,
            variation
        ])


print("Dataset frais généré.")