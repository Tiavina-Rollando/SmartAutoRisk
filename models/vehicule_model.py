from database.db import get_connection


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


def search_vehicules(nom,marque, modele, annee):

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
            av.degat,
            av.role
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
    """
    Supprime un véhicule de la base à partir de son ID
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Supprimer d'abord les éventuels liens avec les accidents
    cursor.execute("DELETE FROM accident_vehicules WHERE vehicule_id = %s", (vehicule_id,))

    # Supprimer le véhicule
    cursor.execute("DELETE FROM vehicules WHERE id = %s", (vehicule_id,))

    conn.commit()
    cursor.close()
    conn.close()


# ==============================
# Ajout
# ==============================
def ajouter_vehicule(proprietaire_id, marque, modele, puissance, cylindre, type, nombre_place, usage, valeur, immatriculation, annee):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO vehicules (proprietaire_id, marque, modele, puissance, cylindre, type, nombre_place, `usage`, valeur, immatriculation, annee)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql,
                   (proprietaire_id,
                    marque,
                    modele,
                    puissance,
                    cylindre,
                    type,
                    nombre_place,
                    usage,
                    valeur,
                    immatriculation,
                    annee))

    conn.commit()
    new_id = cursor.lastrowid  # Récupérer l'ID du véhicule ajouté
    cursor.close()
    conn.close()

    return new_id