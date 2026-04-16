from models.vehicule_model import *


def charger_vehicules():
    return get_all_vehicules()

def rechercher_vehicules(nom,marque, modele, annee):
    return search_vehicules(nom, marque, modele, annee)

def charger_detail_vehicule(vehicule_id):
    return get_detail_vehicule(vehicule_id)

def charger_accidents_vehicule(vehicule_id):
    return get_accidents_vehicule(vehicule_id)

def supprimer_vehicule_db(vehicule_id):
    return supprimer_vehicule(vehicule_id)

def ajouter_vehicule_db(proprietaire_id, marque, modele, puissance, cylindre, type, nombre_place, usage, valeur, immatriculation, annee):
    return ajouter_vehicule(proprietaire_id, marque, modele, puissance, cylindre, type, nombre_place, usage, valeur, immatriculation, annee)