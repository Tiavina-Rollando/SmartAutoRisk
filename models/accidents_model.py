from database.db import get_connection

def get_all_accidents():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM accidents ORDER BY date DESC")
    data = cursor.fetchall()

    conn.close()
    return data

def get_accident_by_id(accident_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM accidents WHERE id = %s", (accident_id,))
    data = cursor.fetchone()

    conn.close()
    return data

def add_accident(date_acc, lieu, type_acc):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO accidents (date, lieu, type)
        VALUES (%s, %s, %s)
    """, (date_acc, lieu, type_acc))

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return new_id

def update_accident(accident_id, date_acc, lieu, type_acc):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE accidents
        SET date=%s, lieu=%s, type=%s
        WHERE id=%s
    """, (date_acc, lieu, type_acc, accident_id))

    conn.commit()
    conn.close()

def delete_accident(accident_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Supprimer les liaisons d'abord
    cursor.execute("DELETE FROM accident_vehicule WHERE accident_id=%s", (accident_id,))
    cursor.execute("DELETE FROM accidents WHERE id=%s", (accident_id,))

    conn.commit()
    conn.close()