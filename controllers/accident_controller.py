from models.accidents_model import *
from models.accident_vehicule_model import *

# ================= FONCTIONS ACCIDENTS =================

def charger_accidents():
    return get_all_accidents()

def charger_accident(accident_id):
    return get_accident_by_id(accident_id)

def ajouter_accident(date_acc, lieu, type_acc):
    return add_accident(date_acc, lieu, type_acc)

def modifier_accident(accident_id, date_acc, lieu, type_acc):
    update_accident(accident_id, date_acc, lieu, type_acc)

def supprimer_accident(accident_id):
    delete_accident(accident_id)


# ================= FONCTIONS ACCIDENT_VEHICULE =================

def charger_accidents_vehicules():
    return get_all_accident_vehicules()

def charger_accidents_par_vehicule(vehicule_id):
    return get_accidents_by_vehicule(vehicule_id)

def ajouter_accident_vehicule(accident_id, vehicule_id, degat, responsabilite, role, valeur):
    return add_accident_vehicule(accident_id, vehicule_id, degat, responsabilite, role, valeur)

def modifier_accident_vehicule(av_id, accident_id, vehicule_id, degat, responsabilite, role, valeur):
    update_accident_vehicule(av_id, accident_id, vehicule_id, degat, responsabilite, role, valeur)

def supprimer_accident_vehicule(av_id):
    delete_accident_vehicule(av_id)


# ================= FONCTION COMBINÉE (LOGIQUE MÉTIER) =================

def enregistrer_accident_complet(date_acc, lieu, type_acc, vehicule_id, degat, responsabilite, role, valeur):
    """
    Crée une entrée dans la table 'accidents' puis lie immédiatement 
    le véhicule concerné dans la table 'accident_vehicule'.
    """
    # 1. Insertion dans la table accidents
    new_accident_id = add_accident(date_acc, lieu, type_acc)

    # 2. Insertion dans la table de liaison accident_vehicule
    new_av_id = add_accident_vehicule(
        accident_id=new_accident_id,
        vehicule_id=vehicule_id,
        degat=degat,
        responsabilite=responsabilite,
        role=role,
        valeur=valeur
    )

    return new_accident_id, new_av_id