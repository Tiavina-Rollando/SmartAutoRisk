from database.db import get_connection

def get_all_contrats():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.*, v.immatriculation, v.marque, v.modele
        FROM contrats c
        JOIN vehicules v ON c.vehicule_id = v.id
        ORDER BY c.date DESC
    """)
    data = cursor.fetchall()

    conn.close()
    return data

def get_contrat_by_vehicule(vehicule_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM contrats WHERE vehicule_id = %s", (vehicule_id,))
    data = cursor.fetchone()

    conn.close()
    return data

def add_contrat(vehicule_id, date_contrat, path, tarif, type_paiement, montant=0.0):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO contrats (vehicule_id, date, path, tarif, type_paiement, montant)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (vehicule_id, date_contrat, path, tarif, type_paiement, montant))
    
    conn.commit()
    contrat_id = cursor.lastrowid
    
    cursor.close()
    conn.close()
    
    return contrat_id

def update_contrat(contrat_id, vehicule_id, date_contrat, path, tarif, type_paiement):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE contrats
        SET vehicule_id=%s, date=%s, path=%s, tarif=%s, type_paiement=%s
        WHERE id=%s
    """, (vehicule_id, date_contrat, path, tarif, type_paiement, contrat_id))

    conn.commit()
    conn.close()

def delete_contrat(contrat_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM contrats WHERE id=%s", (contrat_id,))

    conn.commit()
    conn.close()