from database.db import get_connection

def get_all_clients():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM proprietaires")
    data = cursor.fetchall()

    conn.close()
    return data


def add_client(nom, prenom, naissance, permis, adresse, sexe, aptitude):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO proprietaires(nom, prenom, date_naissance, date_permis, adresse, sexe, aptitude_conduite)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (nom, prenom, naissance, permis, adresse, sexe, aptitude))


    conn.commit()

    new_id = cursor.lastrowid  # ✅ récupérer AVANT fermeture

    conn.close()

    return new_id


def update_client(id, nom, prenom, naissance, permis, adresse, sexe, aptitude):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE proprietaires
        SET nom=%s, prenom=%s, date_naissance=%s, date_permis=%s, adresse=%s, sexe=%s, aptitude_conduite=%s
        WHERE id=%s
    """, (nom, prenom, naissance, permis, adresse, sexe, aptitude, id))

    conn.commit()
    conn.close()


def delete_client(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM vehicules WHERE proprietaire_id=%s", (id,))
    cursor.execute("DELETE FROM proprietaires WHERE id=%s", (id,))

    conn.commit()
    conn.close()