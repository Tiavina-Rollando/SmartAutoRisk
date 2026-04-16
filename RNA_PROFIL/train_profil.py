import csv
from rna_profil import NeuralNetwork


def normalize(sexe,age,anciennete,aptitude):

    age=age/100
    anciennete=anciennete/50

    return [sexe,age,anciennete,aptitude]


def one_hot(label):

    vec=[0,0,0]
    vec[label]=1

    return vec


data=[]

with open("../data/dataset_profil.csv") as f:

    reader=csv.reader(f)

    next(reader)

    for row in reader:

        sexe=int(row[0])
        age=int(row[1])
        anciennete=int(row[2])
        aptitude=int(row[3])
        profil=int(row[4])

        x=normalize(sexe,age,anciennete,aptitude)
        y=one_hot(profil)

        data.append((x,y))


nn=NeuralNetwork(4,5,3)


for epoch in range(5000):

    for x,y in data:

        nn.train(x,y)


print("Training terminé")

nn.save_model("../models/profil_model.json")

test=[0,0.25,0.06,0]

pred=nn.predict(test)

print("Profil prédit :",pred)