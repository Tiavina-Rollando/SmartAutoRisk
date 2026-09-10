import csv
from rna_risk import NeuralNetwork

# --------------------------
# Normalisation des entrées
# --------------------------
def normalize(profil, mois, puissance_vehicule, annee_vehicule,
              type_vehicule, type_saison, periode, taux_accidents_fautifs):

    return [
        profil / 2,                      # 0,1,2 -> 0.0-1.0
        mois / 12,                        # 1-12 -> 0.08-1
        puissance_vehicule / 400,         # 50-400 -> 0.125-1
        1 - (annee_vehicule - 1800) / (2025 - 1800),    # 1800-2026 -> 1-0
        type_vehicule,                    # 0 ou 1
        type_saison,                      # 0 ou 1
        periode / 2,                      # 0,1,2 -> 0-1
        taux_accidents_fautifs            # 0-1 -> 0-1
    ]

# --------------------------
# One-hot pour labels
# --------------------------
def one_hot(label):
    v = [0, 0, 0]
    v[label] = 1
    return v

# --------------------------
# Chargement du dataset
# --------------------------
data = []

with open("../data/dataset_risk.csv") as f:
    reader = csv.reader(f)
    next(reader)  # skip header

    for row in reader:
        profil = int(row[0])
        mois = int(row[1])
        puissance_vehicule = int(row[2])
        annee_vehicule = int(row[3])
        type_vehicule = int(row[4])
        type_saison = int(row[5])
        periode = int(row[6])
        taux_accidents_fautifs = float(row[7])
        risque = int(row[8])

        x = normalize(profil, mois, puissance_vehicule, annee_vehicule,
                      type_vehicule, type_saison, periode,taux_accidents_fautifs)
        y = one_hot(risque)

        data.append((x, y))

# --------------------------
# Initialisation du réseau
# --------------------------
nn = NeuralNetwork(input_size=8, hidden_size=10, output_size=3)

# --------------------------
# Entraînement
# --------------------------
for epoch in range(6000):
    for x, y in data:
        nn.train(x, y)

print("Entraînement terminé")

# --------------------------
# Sauvegarde du modèle
# --------------------------
nn.save_model("../models/risk_model.json")

# --------------------------
# Test rapide
# --------------------------
test_input = normalize(
    profil=2,
    mois=11,
    puissance_vehicule=220,
    annee_vehicule=2018,
    type_vehicule=1,
    type_saison=1,
    periode=2,
    taux_accidents_fautifs=0.3
)

prediction = nn.predict(test_input)
print("Risque prédit :", prediction)