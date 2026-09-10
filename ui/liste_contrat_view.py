import tkinter as tk
from tkinter import ttk, messagebox
from controllers.contrat_controller import recuperer_liste_contrats, resilier_contrat


class ListeContratView(tk.Toplevel):
    """Vue dédiée à la liste et à la consultation des contrats enregistrés."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("SmartAutoRisk - Liste des Contrats")
        self.geometry("900x500")
        self.configure(bg="#ecf0f1")

        self.creer_widgets()
        self.charger_donnees()

    def creer_widgets(self):
        # Header
        header = tk.Frame(self, bg="#2c3e50", height=50)
        header.pack(fill="x")
        tk.Label(
            header, text="GESTION DES CONTRATS ENREGISTRÉS", 
            bg="#2c3e50", fg="white", font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        # Container principal
        container = tk.Frame(self, bg="#ecf0f1")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Tableau (Treeview)
        columns = ("id", "date", "client", "immat", "vehicule", "formule", "montant", "paiement")
        self.tree = ttk.Treeview(container, columns=columns, show="headings", height=12)

        self.tree.heading("id", text="N°")
        self.tree.heading("date", text="Date")
        self.tree.heading("client", text="Propriétaire")
        self.tree.heading("immat", text="Immatriculation")
        self.tree.heading("vehicule", text="Véhicule")
        self.tree.heading("formule", text="Formule")
        self.tree.heading("montant", text="Montant (MGA)")
        self.tree.heading("paiement", text="Paiement")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("date", width=90, anchor="center")
        self.tree.column("client", width=150, anchor="w")
        self.tree.column("immat", width=110, anchor="center")
        self.tree.column("vehicule", width=120, anchor="w")
        self.tree.column("formule", width=80, anchor="center")
        self.tree.column("montant", width=110, anchor="e")
        self.tree.column("paiement", width=100, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Double-clic sur une ligne pour voir les détails
        self.tree.bind("<Double-1>", self.afficher_details_contrat)

        # Barre d'actions en bas
        frame_btn = tk.Frame(self, bg="#ecf0f1")
        frame_btn.pack(fill="x", padx=15, pady=10)

        tk.Button(
            frame_btn, text="Infos Détaillées", command=self.afficher_details_contrat,
            bg="#2e6de6", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", padx=10
        ).pack(side="left")

        tk.Button(
            frame_btn, text="Résilier Contrat", command=self.supprimer_contrat,
            bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", padx=10
        ).pack(side="right")

    def charger_donnees(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.contrats_data = recuperer_liste_contrats()
        for c in self.contrats_data:
            client_nom = f"{c.get('prop_nom', '')} {c.get('prop_prenom', '')}".strip() or "N/A"
            vehicule_str = f"{c.get('marque', '')} {c.get('modele', '')}".strip() or "N/A"
            
            self.tree.insert("", "end", iid=c['contrat_id'], values=(
                c['contrat_id'],
                c['date_creation'],
                client_nom,
                c.get('immatriculation') or "N/A",
                vehicule_str,
                c['formule'],
                f"{c['montant']:,}",
                c['type_paiement']
            ))

    def afficher_details_contrat(self, event=None):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un contrat dans la liste.")
            return

        contrat_id = int(selected[0])
        contrat_info = next((c for c in self.contrats_data if c['contrat_id'] == contrat_id), None)

        if contrat_info:
            FenetreDetailsContrat(self, contrat_info)

    def supprimer_contrat(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un contrat à résilier.")
            return

        contrat_id = int(selected[0])
        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir résilier le contrat N°{contrat_id} ?"):
            resilier_contrat(contrat_id)
            messagebox.showinfo("Succès", "Le contrat a été résilié.")
            self.charger_donnees()


class FenetreDetailsContrat(tk.Toplevel):
    """Fenêtre Pop-up affichant les détails Client, Véhicule et Contrat."""
    def __init__(self, parent, data):
        super().__init__(parent)
        self.title(f"Détails Contrat N°{data['contrat_id']}")
        self.geometry("450x480")
        self.configure(bg="white")
        self.resizable(False, False)

        # Header
        tk.Label(
            self, text=f"Fiche Contrat N°{data['contrat_id']}", 
            font=("Segoe UI", 14, "bold"), bg="white", fg="#2c3e50"
        ).pack(pady=15)

        container = tk.Frame(self, bg="white", padx=20)
        container.pack(fill="both", expand=True)

        def ajouter_section(titre):
            lbl = tk.Label(container, text=titre, font=("Segoe UI", 11, "bold"), fg="#2e6de6", bg="white", anchor="w")
            lbl.pack(fill="x", pady=(10, 2))

        def ajouter_ligne(label, valeur):
            f = tk.Frame(container, bg="white")
            f.pack(fill="x", pady=2)
            tk.Label(f, text=label + " :", font=("Segoe UI", 10, "bold"), bg="white", width=18, anchor="w").pack(side="left")
            tk.Label(f, text=valeur, font=("Segoe UI", 10), bg="white", anchor="w").pack(side="left")

        # 1. Infos Client
        ajouter_section("Informations Client")
        ajouter_ligne("Nom & Prénom", f"{data.get('prop_nom', '')} {data.get('prop_prenom', '')}".strip() or "N/A")

        # 2. Infos Véhicule
        ajouter_section("Informations Véhicule")
        ajouter_ligne("Immatriculation", data.get("immatriculation") or "N/A")
        ajouter_ligne("Marque / Modèle", f"{data.get('marque', '')} {data.get('modele', '')}".strip() or "N/A")

        # 3. Infos Contrat
        ajouter_section("📄 Conditions du Contrat")
        ajouter_ligne("Date souscription", str(data.get("date_creation", "N/A")))
        ajouter_ligne("Formule souscrite", str(data.get("formule", "")).capitalize())
        ajouter_ligne("Mode de paiement", str(data.get("type_paiement", "N/A")))
        ajouter_ligne("Montant réglé", f"{data.get('montant', 0):,} MGA")

        tk.Button(
            self, text="Fermer", command=self.destroy,
            bg="#2c3e50", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=5
        ).pack(pady=15)