from models.proprietaire_model import *

def charger_clients():
    return get_all_clients()

def ajouter_client(nom, prenom, naissance, permis, adresse, sexe, aptitude):
    return add_client(nom, prenom, naissance, permis, adresse, sexe, aptitude)

def modifier_client(id, nom, prenom, naissance, permis, adresse, sexe, aptitude):
    update_client(id, nom, prenom, naissance, permis, adresse, sexe, aptitude)

def supprimer_client(id):
    delete_client(id)