class PaiementView:
    
    @staticmethod
    def menu():

        print("\n===================================")
        print("      GESTION DES PAIEMENTS")
        print("===================================")
        print("1. Ajouter un paiement")
        print("2. Modifier un paiement")
        print("3. Supprimer un paiement")
        print("4. Rechercher un paiement")
        print("5. Afficher tous les paiements")
        print("6. Paiements en attente")
        print("0. Retour")
        print("===================================")

        choix = input("Votre choix : ")

        return choix
    
    @staticmethod
    def saisir_paiement():

        print("\n===== AJOUT D'UN PAIEMENT =====")

        facture_id = input("ID de la facture : ")
        date_paiement = input("Date de paiement (AAAA-MM-JJ) : ")
        montant = input("Montant : ")
        mode_paiement = input("Mode de paiement : ")
        reference = input("Référence : ")

        print("\nStatut :")
        print("1. En attente")
        print("2. Payé")
        print("3. Annulé")

        choix = input("Choix : ")

        if choix == "1":
            statut = "En attente"
        elif choix == "2":
            statut = "Payé"
        elif choix == "3":
            statut = "Annulé"
        else:
            statut = "En attente"

        return (
            facture_id,
            date_paiement,
            montant,
            mode_paiement,
            reference,
            statut
        )