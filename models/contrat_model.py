#import mysql.connector
from database.db import get_connection

class ContratModel:
    """
    Gestionnaire d'accès direct BDD pour la table 'contrats'.
    """

    @staticmethod
    def save(vehicule_id, date_creation, path_pdf, tarif, type_paiement):
        """
        Insère un contrat dans la table 'contrats' (avec 's').
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO contrats (vehicule_id, date, path, tarif, type_paiement)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (vehicule_id, date_creation, path_pdf, tarif, type_paiement))
        conn.commit()
        
        contrat_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        return contrat_id

    @staticmethod
    def get_all_contrats_complets():
        """
        Récupère tous les contrats avec les jointures véhicules et propriétaires.
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                c.id AS contrat_id,
                c.date AS date_creation,
                c.path AS chemin_pdf,
                c.tarif,
                c.type_paiement,
                
                -- Informations Véhicule
                v.id AS vehicule_id,
                v.immatriculation,
                v.marque,
                v.modele,
                v.valeur,
                
                -- Informations Client (Propriétaire)
                p.id AS proprio_id,
                p.nom AS proprio_nom,
                p.prenom AS proprio_prenom,
                p.adresse AS proprio_adresse,
                p.aptitude_conduite AS proprio_aptitude
            FROM contrats c
            LEFT JOIN véhicules v ON c.vehicule_id = v.id
            LEFT JOIN propriétaires p ON v.proprietaire_id = p.id
            ORDER BY c.id DESC
        """
        cursor.execute(query)
        contrats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return contrats