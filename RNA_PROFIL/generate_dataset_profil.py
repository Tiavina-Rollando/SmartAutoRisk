import random
import csv

N = 2000

def calcul_profil(sexe, age, anciennete, aptitude):

    score = 0

    # âge
    if 18 <= age < 40:
        score += 2
    elif 40 <= age < 60:
        score += 1
    else:  # <18 ou >=60
        score -= 2

    # expérience
    if anciennete < 3:
        score -= 2
    elif 3 <= anciennete < 5:
        score += 1
    else:  # >= 5
        score += 2

    # aptitude physique
    if aptitude == 1:
        score += 2   # augmenté pour plus d’impact
    else:
        score -= 2

    # sexe (optionnel selon ton contexte réel)
    if sexe == 1:  # homme
        score += 1
    else:  # femme
        score -= 1  # neutre (plus équitable)

    # décision
    if score <= 0:
        return 2   # risqué
    elif score <= 4:
        return 1   # normal
    else:
        return 0   # prudent


with open("../data/dataset_profil.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "sexe",
        "age_conducteur",
        "anciennete_permis",
        "aptitude_conduite",
        "profil"
    ])

    for _ in range(N):
        sexe = random.randint(0, 1)

        age = random.randint(18, 75)

        anciennete = random.randint(0, age - 18)

        aptitude = random.randint(0, 1)

        profil = calcul_profil(sexe, age, anciennete, aptitude)

        writer.writerow([sexe, age, anciennete, aptitude, profil])


print("Dataset profil généré.")