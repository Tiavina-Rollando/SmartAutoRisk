import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

from models.factures_model import (
    add_facture, 
    update_path_facture, 
    get_factures_by_contrat,
    get_contrat_details_for_facture
)
from services.pdf_generator import generer_pdf_facture


def calculer_plage_fin(plage_deb_str, type_paiement):
    """Calcule la date de fin de couverture."""
    date_debut = datetime.strptime(plage_deb_str, "%Y-%m-%d")
    type_p = str(type_paiement).lower() if type_paiement else "annuel"

    if "mensuel" in type_p:
        date_fin = date_debut + relativedelta(months=1)
    elif "trimestriel" in type_p:
        date_fin = date_debut + relativedelta(months=3)
    elif "semestriel" in type_p:
        date_fin = date_debut + relativedelta(months=6)
    else:  # Annuel
        date_fin = date_debut + relativedelta(years=1)

    return date_fin.strftime("%Y-%m-%d")


def calculer_montant_echeance(tarif_total, type_paiement):
    """
    Calcule le montant de l'échéance.
    Divise par 3 pour les contrats semestriels.
    """
    type_p = str(type_paiement).lower() if type_paiement else "annuel"
    
    try:
        montant_float = float(tarif_total) if tarif_total is not None else 0.0
    except (ValueError, TypeError):
        montant_float = 0.0

    if "semestriel" in type_p:
        diviseur = 3  # Divisé par 3 selon votre règle métier
    elif "trimestriel" in type_p:
        diviseur = 4
    elif "mensuel" in type_p:
        diviseur = 12
    else:
        diviseur = 1

    return round(montant_float / diviseur, 2)


def creer_nouveau_paiement(contrat_id, plage_deb, commentaire="Paiement effectue"):
    """Enregistre un paiement et génère la facture PDF."""
    details = get_contrat_details_for_facture(contrat_id)
    
    if not details:
        raise ValueError(f"Aucun contrat trouvé pour l'ID {contrat_id}")

    # FIX: Récupération de la colonne 'montant' (numérique) et non 'tarif' (texte)
    tarif_contrat = details.get("montant", 0.0)
    type_paiement = details.get("type_paiement", "annuel")

    # Calcul du montant de la facture
    frais_montant = calculer_montant_echeance(tarif_contrat, type_paiement)
    plage_fin = calculer_plage_fin(plage_deb, type_paiement)

    date_paiement = datetime.now().strftime("%Y-%m-%d")

    # Insertion en base
    facture_id = add_facture(
        date_facture=date_paiement,
        plage_deb=plage_deb,
        plage_fin=plage_fin,
        contrat_id=contrat_id,
        frais=frais_montant,
        path="",
        statut=1,
        commentaire=commentaire
    )

    # Génération du fichier PDF
    nom_vehicule = f"{details.get('marque', '')} {details.get('modele', '')}".strip()
    pdf_path = generer_pdf_facture(
        facture_id=facture_id,
        date_facture=date_paiement,
        plage_deb=plage_deb,
        plage_fin=plage_fin,
        proprio_nom=details.get("nom", ""),
        proprio_prenom=details.get("prenom", ""),
        immatriculation=details.get("immatriculation", ""),
        nom_vehicule=nom_vehicule,
        montant=frais_montant
    )

    update_path_facture(facture_id, pdf_path)

    return facture_id


def lister_factures_contrat(contrat_id):
    return get_factures_by_contrat(contrat_id)