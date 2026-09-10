import csv
from rna_rate import NeuralNetwork


def normalize(niveau, type, places, usage, tarif, valeur):

    niveau=niveau/2
    type=type
    places=places/30
    usage=usage
    tarif=tarif
    if type == 0:  # moto
        valeur=valeur/50000
    else:  # voiture
        valeur=valeur/100000

    return [niveau,type,places,usage,tarif,valeur]


data=[]

with open("../data/dataset_rate.csv") as f:

    reader=csv.reader(f)

    next(reader)

    for row in reader:

        niveau=int(row[0])
        type=int(row[1])
        places=int(row[2])
        usage=int(row[3])
        tarif=int(row[4])
        valeur=float(row[5])
        variation=float(row[6])
        x=normalize(niveau,type,places,usage,tarif,valeur)

        data.append((x,variation))


nn=NeuralNetwork(6,6)


for epoch in range(8000):

    for x,y in data:

        nn.train(x,y)


print("Entrainement terminé")

nn.save_model("../models/rate_model.json")

test=normalize(0,1,5,0,0,20000)

prediction=nn.predict(test)

print("Variation frais prédite :",prediction)