import random
import csv

N = 2000  # nombre de lignes


def calcul_niveau_risque(
    profil,
    puissance_vehicule,
    annee_vehicule,
    type_vehicule,
    type_saison,
    periode,
    taux_accidents_fautifs,
):

    score = 0

    # Impact du profil conducteur
    score += profil * 2  # profil plus risqué = score plus élevé

    # Véhicule puissant = plus de risque
    if puissance_vehicule < 70 and type_vehicule == 1:  # voiture faible puissance
        score -= 2
    elif puissance_vehicule > 70 and puissance_vehicule < 120 and type_vehicule == 1:  # voiture moyenne puissance
        score -= 1
    elif puissance_vehicule > 120 and puissance_vehicule < 200 and type_vehicule == 1:  # voiture forte puissance
        score += 1
    elif puissance_vehicule > 200 and type_vehicule == 1:  # voiture très forte puissance
        score += 2
    elif puissance_vehicule < 15 and type_vehicule == 0:  # moto faible puissance
        score -= 2
    elif puissance_vehicule >= 15 and puissance_vehicule < 35 and type_vehicule == 0:  # moto moyenne puissance
        score -= 1
    elif puissance_vehicule >= 35 and puissance_vehicule < 70 and type_vehicule == 0:  # moto forte puissance
        score += 1
    elif puissance_vehicule >= 70 and type_vehicule == 0:  # moto très forte puissance   
        score += 2

    # Véhicule ancien = moins sûr
    if annee_vehicule < 2005:
        score += 2
    elif annee_vehicule < 2015 and annee_vehicule >= 2005:
        score += 1
    elif annee_vehicule >= 2015:
        score -= 1

    # Type véhicule
    if type_vehicule == 0:  # moto
        score += 2
    elif type_vehicule == 1:  # voiture
        score += 1

    # Saison pluvieuse
    if type_saison == 1:  # pluvieux
        score += 1
    elif type_saison == 0:  # sec
        score -= 1

    # Période de circulation
    if periode == 1:  # fête
        score += 2
    elif periode == 2:  # vacances
        score += 1
    elif periode == 0:  # calme
        score -= 2

    # Taux d'accidents fautifs
    if taux_accidents_fautifs == 0:
        score -= 2
    elif taux_accidents_fautifs < 0.5 and taux_accidents_fautifs > 0:
        score += 1
    elif taux_accidents_fautifs >= 0.5:
        score += 2

    # Décision finale
    if score <= -2:
        return 0  # très faible
    elif score <= 3:
        return 0  # faible
    elif score <= 7:
        return 1  # moyen
    else:
        return 2  # élevé

with open("../data/dataset_risk.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "profil",
        "mois",
        "puissance_vehicule",
        "annee_vehicule",
        "type_vehicule",
        "type_saison",
        "periode",
        "taux_accidents_fautifs",
        "niveau_risque"
    ])

    for _ in range(N):

        profil = random.randint(0, 2)

        mois = random.randint(1, 12)

        puissance_vehicule = random.randint(50, 400)

        annee_vehicule = random.randint(1800, 2026)

        type_vehicule = random.randint(0, 1)  # 0 moto / 1 voiture

        type_saison = random.randint(0, 1)  # 0 sec / 1 pluvieux

        periode = random.randint(0, 2)  # 0 calme / 1 fête / 2 vacances

        taux_accidents_fautifs = random.uniform(0, 1)

        niveau = calcul_niveau_risque(
            profil,
            puissance_vehicule,
            annee_vehicule,
            type_vehicule,
            type_saison,
            periode,
            taux_accidents_fautifs
        )

        writer.writerow([
            profil,
            mois,
            puissance_vehicule,
            annee_vehicule,
            type_vehicule,
            type_saison,
            periode,
            taux_accidents_fautifs,
            niveau
        ])

print("Dataset généré avec succès.")