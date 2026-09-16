from database.db import get_connection

def add_facture(date_facture, plage_deb, plage_fin, contrat_id, frais, path, statut=0, commentaire=""):
    """
    Insère une nouvelle facture rattachée à un contrat.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO factures (date, plage_deb, plage_fin, contrat_id, frais, path, statut, commentaire)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        date_facture,
        plage_deb,
        plage_fin,
        contrat_id,
        frais,
        path,
        statut,
        commentaire
    ))

    conn.commit()
    facture_id = cursor.lastrowid
    conn.close()

    return facture_id


def get_factures_by_contrat(contrat_id):
    """
    Récupère toutes les factures associées à un contrat spécifique.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM factures 
        WHERE contrat_id = %s 
        ORDER BY plage_deb ASC
    """, (contrat_id,))

    data = cursor.fetchall()
    conn.close()

    return data


def get_facture_by_id(facture_id):
    """
    Récupère une facture par son ID avec les informations du contrat et du véhicule.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT f.*, c.tarif, c.type_paiement, v.immatriculation, v.marque, v.modele, p.nom, p.prenom
        FROM factures f
        JOIN contrats c ON f.contrat_id = c.id
        JOIN vehicules v ON c.vehicule_id = v.id
        JOIN proprietaires p ON v.proprietaire_id = p.id
        WHERE f.id = %s
    """

    cursor.execute(query, (facture_id,))
    data = cursor.fetchone()
    conn.close()

    return data


def update_statut_facture(facture_id, statut):
    """
    Met à jour le statut de paiement d'une facture (1 = Payée, 0 = Non payée).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE factures 
        SET statut = %s 
        WHERE id = %s
    """, (statut, facture_id))

    conn.commit()
    conn.close()


def update_path_facture(facture_id, path):
    """
    Met à jour le chemin (path) du fichier PDF associé à la facture.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE factures 
        SET path = %s 
        WHERE id = %s
    """, (path, facture_id))

    conn.commit()
    conn.close()


def delete_facture(facture_id):
    """
    Supprime une facture à partir de son ID.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM factures WHERE id = %s", (facture_id,))

    conn.commit()
    conn.close()


def get_contrat_details_for_facture(contrat_id):
    """
    Récupère les détails du contrat actif et les informations associées.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            c.id AS contrat_id, 
            c.type_paiement, 
            COALESCE(c.tarif, 0.0) AS tarif,
            v.immatriculation, v.marque, v.modele,
            p.nom, p.prenom
        FROM contrats c
        JOIN vehicules v ON c.vehicule_id = v.id
        LEFT JOIN proprietaires p ON v.proprietaire_id = p.id
        WHERE c.id = %s
    """

    cursor.execute(query, (contrat_id,))
    data = cursor.fetchone()
    conn.close()

    return data


def get_contrat_details_for_facture(contrat_id):
    """
    Récupère les détails du contrat, le montant exact (c.montant),
    ainsi que les infos du véhicule et du propriétaire.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            c.id AS contrat_id, 
            c.type_paiement, 
            c.tarif AS offre_nom,
            COALESCE(c.montant, 0.0) AS montant,
            v.immatriculation, v.marque, v.modele,
            p.nom, p.prenom
        FROM contrats c
        JOIN vehicules v ON c.vehicule_id = v.id
        LEFT JOIN proprietaires p ON v.proprietaire_id = p.id
        WHERE c.id = %s
    """

    cursor.execute(query, (contrat_id,))
    data = cursor.fetchone()
    conn.close()

    return data