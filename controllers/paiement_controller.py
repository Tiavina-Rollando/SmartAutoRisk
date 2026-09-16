import mysql.connector
from mysql.connector import Error


class PaiementController:

    @staticmethod
    def get_connection():
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="smartautorisk"
        )


    @classmethod
    def update(cls, paiement_id, facture_id, date_paiement,
               montant, mode_paiement, reference, statut):

        conn = cls.get_connection()
        cursor = conn.cursor()

        try:

            query = """
                UPDATE paiements
                SET
                    facture_id = %s,
                    date_paiement = %s,
                    montant = %s,
                    mode_paiement = %s,
                    reference = %s,
                    statut = %s
                WHERE id = %s
            """

            cursor.execute(
                query,
                (
                    facture_id,
                    date_paiement,
                    montant,
                    mode_paiement,
                    reference,
                    statut,
                    paiement_id
                )
            )

            conn.commit()

            return True

        except Error as err:
            print(f"Erreur de modification : {err}")
            return False

        finally:
            cursor.close()
            conn.close()


    @classmethod
    def delete(cls, paiement_id):

        conn = cls.get_connection()
        cursor = conn.cursor()

        try:

            query = """
                DELETE FROM paiements
                WHERE id = %s
            """

            cursor.execute(query, (paiement_id,))

            conn.commit()

            return True

        except Error as err:
            print(f"Erreur de suppression : {err}")
            return False

        finally:
            cursor.close()
            conn.close()


    @classmethod
    def search(cls, paiement_id):

        conn = cls.get_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT *
                FROM paiements
                WHERE id = %s
            """

            cursor.execute(query, (paiement_id,))

            return cursor.fetchone()

        except Error as err:
            print(f"Erreur de recherche : {err}")
            return None

        finally:
            cursor.close()
            conn.close()


    @classmethod
    def read_pending(cls):

        conn = cls.get_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT *
                FROM paiements
                WHERE statut = 'En attente'
                ORDER BY date_paiement DESC
            """

            cursor.execute(query)

            return cursor.fetchall()

        except Error as err:
            print(f"Erreur de lecture : {err}")
            return []

        finally:
            cursor.close()
            conn.close()