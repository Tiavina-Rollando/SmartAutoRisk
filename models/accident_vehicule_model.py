from database.db import get_connection

def get_all_accident_vehicules():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT av.*, a.date, a.lieu, a.type AS type_accident, v.immatriculation, v.marque, v.modele
        FROM accident_vehicules av
        JOIN accidents a ON av.accident_id = a.id
        JOIN vehicules v ON av.vehicule_id = v.id
        ORDER BY a.date DESC
    """)
    data = cursor.fetchall()

    conn.close()
    return data

def get_accidents_by_vehicule(vehicule_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT av.*, a.date, a.lieu, a.type AS type_accident
        FROM accident_vehicules av
        JOIN accidents a ON av.accident_id = a.id
        WHERE av.vehicule_id = %s
    """, (vehicule_id,))
    data = cursor.fetchall()

    conn.close()
    return data

def add_accident_vehicule(accident_id, vehicule_id, degat, responsabilite, role, valeur):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO accident_vehicules (accident_id, vehicule_id, degat, responsabilite, role, valeur)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (accident_id, vehicule_id, degat, responsabilite, role, valeur))

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return new_id

def update_accident_vehicule(av_id, accident_id, vehicule_id, degat, responsabilite, role, valeur):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE accident_vehicules
        SET accident_id=%s, vehicule_id=%s, degat=%s, responsabilite=%s, role=%s, valeur=%s
        WHERE id=%s
    """, (accident_id, vehicule_id, degat, responsabilite, role, valeur, av_id))

    conn.commit()
    conn.close()

def delete_accident_vehicule(av_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM accident_vehicules WHERE id=%s", (av_id,))

    conn.commit()
    conn.close()