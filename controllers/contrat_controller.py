from database.db import get_connection
from datetime import datetime, date, timedelta
from models.contrat_model import add_contrat
from services.pdf_generator import generer_pdf_contrat

MAP_TYPE_PAIEMENT = {
    "Trimestre": "trimestriel",
    "Semestre": "semestriel",
    "Annuel": "annuel",
    "Mensuel": "mensuel"
}


def get_montant_total_vehicule(vehicule_id):
    """
    Calcule la somme des frais sur les 12 derniers mois.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Date d'il y a 365 jours au format DATETIME complet
    date_limite = datetime.now() - timedelta(days=365)

    query = """
        SELECT COALESCE(SUM(f.frais), 0)
        FROM historique_niveau_risks r
        JOIN historique_frais f ON r.id = f.historique_niveau_risk_id
        WHERE r.vehicule_id = %s AND r.date_evaluation >= %s
    """
    
    cursor.execute(query, (vehicule_id, date_limite))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()

    return float(result[0]) if result and result[0] else 0.0


def creer_contrat_vehicule(vehicule_id, offre, modalite_paiement, montant=None):
    from models.vehicule_model import get_detail_vehicule

    type_paiement = MAP_TYPE_PAIEMENT.get(modalite_paiement, "annuel")
    date_actuelle = datetime.now().strftime("%Y-%m-%d")

    # Si le montant n'est pas fourni, calcul automatique via la BDD
    if montant is None:
        montant = get_montant_total_vehicule(vehicule_id)

    # Récupération des détails du véhicule
    details = get_detail_vehicule(vehicule_id)
    
    proprio_nom = details.get("nom", "") if details else ""
    proprio_prenom = details.get("prenom", "") if details else ""
    type_v = details.get("type", "") if details else ""
    
    marque = details.get("marque", "") if details else ""
    modele = details.get("modele", "") if details else ""
    nom_vehicule = f"{marque} {modele}".strip()

    # Génération du PDF
    pdf_path = generer_pdf_contrat(
        vehicule_id=vehicule_id,
        date_contrat=date_actuelle,
        proprio_nom=proprio_nom,
        proprio_prenom=proprio_prenom,
        type_v=type_v,
        nom_vehicule=nom_vehicule,
        offre=offre,
        modalite_paiement=modalite_paiement
    )

    # Sauvegarde du contrat dans la BDD
    contrat_id = add_contrat(
        vehicule_id=vehicule_id,
        date_contrat=date_actuelle,
        path=pdf_path,
        tarif=offre,
        type_paiement=type_paiement,
        montant=montant
    )
    
    return contrat_id