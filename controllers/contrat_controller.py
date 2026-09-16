import os
from database.db import get_connection
from services.pdf_generator import generer_pdf_contrat
from database.db import get_connection
from datetime import datetime, date, timedelta
from models.contrat_model import add_contrat

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

def determiner_saison_actuelle():
    """Détermine la saison en fonction du mois actuel."""
    mois = datetime.now().month
    # Exemple de mapping : 11 à 3 = Saison Pluie/Cyclonique, 4 à 10 = Saison Sèche
    if mois in [11, 12, 1, 2, 3]:
        return "Pluie"
    return "Sèche"


def obtenir_montant_saison_actuelle(vehicule_id, tarif_formule="simple"):
    """
    Calcule le montant exact du véhicule pour la date d'aujourd'hui 
    en fonction de son niveau de risque de la saison actuelle.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Récupération des données du véhicule
    query_vehicule = "SELECT * FROM vehicules WHERE id = %s"
    cursor.execute(query_vehicule, (vehicule_id,))
    vehicule = cursor.fetchone()

    if not vehicule:
        cursor.close()
        conn.close()
        return 0

    saison_actuelle = determiner_saison_actuelle()

    # 2. Récupération du niveau de risque enregistré pour la saison courante
    query_risk = """
        SELECT hnr.niveau_risk 
        FROM historique_niveau_risks hnr
        JOIN saisons s ON hnr.saison_id = s.id
        WHERE hnr.vehicule_id = %s AND s.type = %s
        ORDER BY hnr.date_evaluation DESC LIMIT 1
    """
    cursor.execute(query_risk, (vehicule_id, saison_actuelle))
    risk_data = cursor.fetchone()
    
    niveau_risk = risk_data['niveau_risk'] if risk_data else 1.0

    cursor.close()
    conn.close()

    # 3. Calcul de la formule de frais (identique à la logique métier)
    valeur = float(vehicule.get('valeur', 20000000))
    puissance = float(vehicule.get('puissance', 5))
    
    base_tarif = (valeur * 0.015) + (puissance * 2000)
    
    # Majorations
    coef_formule = 1.35 if tarif_formule.lower() == "prenium" else 1.0
    montant_final = base_tarif * (1 + (niveau_risk * 0.1)) * coef_formule

    return int(montant_final)


def recuperer_liste_vehicules():
    """Récupère la liste de tous les véhicules enregistrés avec le nom du propriétaire."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT v.id, v.immatriculation, v.marque, v.modele, v.valeur, v.nombre_place, v.type,
               p.nom AS prop_nom, p.prenom AS prop_prenom
        FROM vehicules v
        LEFT JOIN proprietaires p ON v.proprietaire_id = p.id
    """
    cursor.execute(query)
    vehicules = cursor.fetchall()
    cursor.close()
    conn.close()
    return vehicules


def creer_nouveau_contrat(vehicule_id, data_vehicule, montant, tarif_formule="simple", type_paiement="Annuel"):
    date_creation = datetime.now().date()
    formule_clean = "prenium" if tarif_formule.lower() == "prenium" else "simple"
    type_paiement_clean = type_paiement.strip()

    # Création du dossier cible si nécessaire
    dossier = os.path.join("data", "contrats")
    os.makedirs(dossier, exist_ok=True)

    # Extraction sécurisée des informations du véhicule/propriétaire depuis data_vehicule
    immat = data_vehicule.get('immatriculation', 'NC')
    proprio_nom = data_vehicule.get('nom_p', 'N/A')
    proprio_prenom = data_vehicule.get('prenom_p', '')
    type_v = data_vehicule.get('type', 'N/A')
    
    # Construction du nom de véhicule (ex: Toyota Corolla)
    marque = data_vehicule.get('marque', '')
    modele = data_vehicule.get('modele', '')
    nom_vehicule = f"{marque} {modele}".strip() or "Inconnu"

    # Initialisation du chemin PDF
    chemin_pdf = ""

    # 1. Tentative de génération du PDF
    try:
        chemin_pdf = generer_pdf_contrat(
            vehicule_id=vehicule_id,
            date_contrat=date_creation,
            proprio_nom=proprio_nom,
            proprio_prenom=proprio_prenom,
            type_v=type_v,
            nom_vehicule=nom_vehicule,
            offre=formule_clean,
            modalite_paiement=type_paiement_clean
        )
    except Exception as pdf_err:
        print(f"[AVERTISSEMENT] Génération PDF échouée : {pdf_err}")
        chemin_pdf = ""

    # 2. Insertion en Base de Données
    # (Si vous utilisez une fonction dédiée add_contrat, vous pouvez utiliser le bloc ci-dessous au lieu de l'accès direct SQL)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO contrats (vehicule_id, date, path, tarif, montant, type_paiement)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            vehicule_id, 
            date_creation, 
            chemin_pdf, 
            formule_clean, 
            int(montant), 
            type_paiement_clean
        ))
        
        conn.commit()
        contrat_id = cursor.lastrowid
        cursor.close()
        conn.close()
    except Exception as db_err:
        print(f"[ERREUR] Échec d'insertion du contrat en BDD : {db_err}")
        return None, chemin_pdf

    return contrat_id, chemin_pdf

def resilier_contrat(contrat_id):
    """Suppression/Résiliation d'un contrat de la BDD."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "DELETE FROM contrats WHERE id = %s"
    cursor.execute(query, (contrat_id,))
    conn.commit()
    cursor.close()
    conn.close()


def recuperer_liste_contrats():
    """Récupère l'historique complet pour la vue Liste des Contrats."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT 
            c.id AS contrat_id,
            c.date AS date_creation,
            c.path AS chemin_pdf,
            c.tarif AS formule,
            c.montant,
            c.type_paiement,
            v.id AS vehicule_id,
            v.immatriculation,
            v.marque,
            v.modele,
            p.nom AS prop_nom,
            p.prenom AS prop_prenom
        FROM contrats c
        LEFT JOIN vehicules v ON c.vehicule_id = v.id
        LEFT JOIN proprietaires p ON v.proprietaire_id = p.id
        ORDER BY c.id DESC
    """
    cursor.execute(query)
    contrats = cursor.fetchall()
    cursor.close()
    conn.close()
    return contrats