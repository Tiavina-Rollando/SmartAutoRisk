import os
from datetime import datetime
from database.db import get_connection
from services.pdf_generator import generer_pdf_contrat


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

    # Création du dossier cible
    dossier = os.path.join("data", "contrats")
    os.makedirs(dossier, exist_ok=True)

    immat = data_vehicule.get('immatriculation', 'NC')
    chemin_pdf = os.path.join(dossier, f"contrat_{vehicule_id}_{immat}.pdf")

    # Tentative d'impression PDF
    try:
        from services.pdf_generator import generer_pdf_contrat
        generer_pdf_contrat(
            output_path=chemin_pdf,
            details=data_vehicule,
            date_signature=str(date_creation),
            tarif=montant,
            type_paiement=type_paiement_clean
        )
    except Exception as pdf_err:
        print(f"[AVERTISSEMENT] Génération PDF échouée : {pdf_err}")
        chemin_pdf = ""

    # Insertion SQL
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