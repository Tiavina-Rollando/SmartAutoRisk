from database.db import get_connection
#from controllers.contrat_controller import creer_contrat_vehicule


def get_all_vehicules():
    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
            SELECT 
                v.id,
                v.immatriculation,
                v.type,
                CONCAT(p.nom, ' ', p.prenom) AS proprietaire,
                v.marque,
                v.modele,
                v.annee
            FROM vehicules v
            JOIN proprietaires p ON v.proprietaire_id = p.id
        """)

    result = cursor.fetchall()

    cursor.close()
    db.close()

    return result


def search_vehicules(nom, marque, modele, annee):
    db = get_connection()
    cursor = db.cursor()

    query = """
            SELECT 
                v.id,
                CONCAT(p.nom, ' ', p.prenom) AS proprietaire,
                v.marque,
                v.modele,
                v.annee
            FROM vehicules v
            JOIN proprietaires p ON v.proprietaire_id = p.id
            WHERE (%s='' OR p.nom=%s)
            AND (%s='' OR v.marque=%s)
            AND (%s='' OR v.modele=%s)
            AND (%s='' OR v.annee=%s)
        """

    cursor.execute(query,
                   (nom, nom,
                    marque, marque,
                    modele, modele,
                    annee, annee))

    result = cursor.fetchall()

    cursor.close()
    db.close()

    return result

# ==============================
# VEHICULE + PROPRIETAIRE
# ==============================
def get_detail_vehicule(vehicule_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT
        v.id,
        v.marque,
        v.modele,
        v.puissance,
        v.type,
        v.nombre_place,
        v.usage,
        v.valeur,
        v.immatriculation,

        p.nom,
        p.prenom,
        p.date_permis,
        p.adresse,
        p.date_naissance,
        p.aptitude_conduite

    FROM vehicules v
    JOIN proprietaires p ON v.proprietaire_id = p.id
    WHERE v.id = %s
    """

    cursor.execute(sql, (vehicule_id,))
    data = cursor.fetchone()

    conn.close()

    return data


def get_accidents_vehicule(vehicule_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    sql = """
        SELECT 
            a.date,
            a.lieu,
            a.gravite,
            a.type,
            av.degat
        FROM accidents a
        JOIN accident_vehicules av 
            ON a.id = av.accident_id
        WHERE av.vehicule_id = %s
        ORDER BY a.date DESC
    """

    cursor.execute(sql, (vehicule_id,))
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result

# ==============================
# Suppression
# ==============================
def supprimer_vehicule(vehicule_id):
    from database.models.base import get_session
    from database.models.vehicule import Vehicule
    from database.models.historique_frais import HistoriqueFrais
    from database.models.accident_vehicule import AccidentVehicule
    from database.models.historique_niveau_risk import HistoriqueNiveauRisk
    from database.models.contrat import Contrat  # Importer le modèle Contrat SQLAlchemy si existant

    session = get_session()

    try:
        vehicule_id = int(vehicule_id)

        # 0. Supprimer contrats liés
        try:
            session.query(Contrat).filter_by(vehicule_id=vehicule_id).delete()
        except Exception:
            # Fallback en requête brute si le modèle SQLAlchemy Contrat n'est pas déclaré
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contrats WHERE vehicule_id = %s", (vehicule_id,))
            conn.commit()
            conn.close()

        # 1. Supprimer accidents liés
        session.query(AccidentVehicule)\
            .filter_by(vehicule_id=vehicule_id)\
            .delete()

        # 2. Récupérer niveaux de risque
        risques = session.query(HistoriqueNiveauRisk)\
            .filter_by(vehicule_id=vehicule_id)\
            .all()

        for risque in risques:
            # 3. Supprimer frais liés à chaque risque
            session.query(HistoriqueFrais)\
                .filter_by(historique_niveau_risk_id=risque.id)\
                .delete()

        # 4. Supprimer niveaux de risque
        session.query(HistoriqueNiveauRisk)\
            .filter_by(vehicule_id=vehicule_id)\
            .delete()

        # 5. Supprimer véhicule
        session.query(Vehicule)\
            .filter_by(id=vehicule_id)\
            .delete()

        session.commit()

    except Exception as e:
        session.rollback()
        print("Erreur suppression :", e)

    finally:
        session.close()

# ==============================
# Ajout
# ==============================
# Dans models/vehicule_model.py

def ajouter_vehicule(proprietaire_id, marque, modele, puissance, cylindre, type, nombre_place, usage, valeur, immatriculation, annee, offre, modalite_paiement):
    # ✅ Import local ici
    from controllers.contrat_controller import creer_contrat_vehicule

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO vehicules (proprietaire_id, marque, modele, puissance, cylindre, type, nombre_place, `usage`, valeur, immatriculation, annee)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql,
                   (proprietaire_id, marque, modele, puissance, cylindre, type, nombre_place, usage, valeur, immatriculation, annee))

    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    # Enregistrement du contrat associé
    #creer_contrat_vehicule(
        #vehicule_id=new_id,
        #offre=offre,
        #modalite_paiement=modalite_paiement
    #)

    return new_id