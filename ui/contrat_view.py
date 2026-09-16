import traceback
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
from controllers.contrat_controller import (
    creer_nouveau_contrat,
    get_montant_total_vehicule,
    recuperer_liste_vehicules
)


class ContratView(tk.Toplevel):
    """Fenêtre de Souscription d'un Contrat d'Assurance."""

    def __init__(self, parent, vehicule_id=None, data_vehicule=None):
        super().__init__(parent)
        self.vehicule_id = vehicule_id
        self.data_vehicule = data_vehicule or {}

        # Configuration de la fenêtre (Agrandie pour projection)
        self.title("Souscription de Contrat d'Assurance")
        self.geometry("580x680")
        self.configure(bg="#F1F5F9")
        self.resizable(False, False)

        # Style TTK pour grandes polices
        self._init_styles()

        self.vehicules_list = recuperer_liste_vehicules()
        self.creer_widgets()

    def _init_styles(self):
        """Configuration du style des Combobox et widgets TTK."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Customisation des Combobox pour la présentation
        self.style.configure(
            "Large.TCombobox",
            font=("Segoe UI", 12),
            padding=6
        )
        self.option_add("*TCombobox*Listbox.font", ("Segoe UI", 12))

    def extraction_montant_du_jour(self):
        frais = self.data_vehicule.get("frais", [])
        mois_actuel = datetime.now().month

        for f in frais:
            if f.get("mois") == mois_actuel:
                return f.get("montant", 0)

        if frais:
            return frais[0].get("montant", 0)

        return self.data_vehicule.get("montant_graphe", 0)

    def creer_widgets(self):
        # Header / Banner Supérieur
        header = tk.Frame(self, bg="#1E293B", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📋  Souscription d'un Contrat",
            font=("Segoe UI", 18, "bold"),
            bg="#1E293B",
            fg="#F8FAFC"
        ).pack(side="left", padx=25)

        # Conteneur Formulaire (Carte blanche)
        card = tk.Frame(self, bg="#FFFFFF", padx=30, pady=25)
        card.pack(fill="both", expand=True, padx=25, pady=20)

        # 1. Sélection du Véhicule
        tk.Label(
            card,
            text="Véhicule concerné :",
            font=("Segoe UI", 12, "bold"),
            bg="#FFFFFF",
            fg="#1E293B",
            anchor="w"
        ).pack(fill="x", pady=(5, 4))

        options_vehicules = [
            f"{v['id']} - {v['immatriculation']} ({v['marque']} {v['modele']})"
            for v in self.vehicules_list
        ]

        self.combo_vehicule = ttk.Combobox(
            card,
            values=options_vehicules,
            state="readonly",
            style="Large.TCombobox"
        )
        self.combo_vehicule.pack(fill="x", ipady=4, pady=(0, 15))
        self.combo_vehicule.bind("<<ComboboxSelected>>", self.recalculer_montant_tarif)

        # 2. Formule / Tarif
        tk.Label(
            card,
            text="Formule d'Assurance :",
            font=("Segoe UI", 12, "bold"),
            bg="#FFFFFF",
            fg="#1E293B",
            anchor="w"
        ).pack(fill="x", pady=(5, 4))

        self.combo_tarif = ttk.Combobox(
            card,
            values=["simple", "prenium"],
            state="readonly",
            style="Large.TCombobox"
        )
        self.combo_tarif.set("prenium" if self.data_vehicule.get('tarif') == "prenium" else "simple")
        self.combo_tarif.pack(fill="x", ipady=4, pady=(0, 15))
        self.combo_tarif.bind("<<ComboboxSelected>>", self.recalculer_montant_tarif)

        # 3. Type de paiement
        tk.Label(
            card,
            text="Fréquence de Paiement :",
            font=("Segoe UI", 12, "bold"),
            bg="#FFFFFF",
            fg="#1E293B",
            anchor="w"
        ).pack(fill="x", pady=(5, 4))

        self.combo_paiement = ttk.Combobox(
            card,
            values=["Annuel", "Semestriel", "Trimestriel", "Mensuel"],
            state="readonly",
            style="Large.TCombobox"
        )
        self.combo_paiement.set("Annuel")
        self.combo_paiement.pack(fill="x", ipady=4, pady=(0, 20))
        self.combo_paiement.bind("<<ComboboxSelected>>", self.recalculer_montant_tarif)

        # Separateur visuel
        tk.Frame(card, bg="#E2E8F0", height=2).pack(fill="x", pady=10)

        # 4. Montant Calculé (En évidence)
        tk.Label(
            card,
            text="Montant de l'échéance (MGA) :",
            font=("Segoe UI", 13, "bold"),
            bg="#FFFFFF",
            fg="#0284C7",
            anchor="w"
        ).pack(fill="x", pady=(5, 4))

        self.entry_montant = tk.Entry(
            card,
            font=("Segoe UI", 16, "bold"),
            fg="#0284C7",
            bg="#F0F9FF",
            bd=1,
            relief="solid",
            justify="center"
        )
        self.entry_montant.pack(fill="x", ipady=8, pady=(0, 20))

        # Pré-sélection du véhicule si fourni
        if self.vehicule_id:
            for idx, v in enumerate(self.vehicules_list):
                if str(v['id']) == str(self.vehicule_id):
                    self.combo_vehicule.current(idx)
                    break
        elif options_vehicules:
            self.combo_vehicule.current(0)

        # Bouton d'action principal
        btn_valider = tk.Button(
            card,
            text="✓  Enregistrer le contrat",
            command=self.valider,
            bg="#10B981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            font=("Segoe UI", 13, "bold"),
            relief="flat",
            cursor="hand2",
            bd=0,
            pady=12
        )
        btn_valider.pack(fill="x")

        self.recalculer_montant_tarif()

    def recalculer_montant_tarif(self, event=None):
        montant_base = self.extraction_montant_du_jour()
        tarif_choisi = self.combo_tarif.get()
        frequence_paiement = self.combo_paiement.get()

        # Majorations de formule
        if tarif_choisi.lower() == "prenium":
            montant_annuel = montant_base * 1.35
        else:
            montant_annuel = montant_base

        # Découpage selon la fréquence de paiement
        diviseurs = {
            "Annuel": 1,
            "Semestriel": 2,
            "Trimestriel": 4,
            "Mensuel": 12
        }
        diviseur = diviseurs.get(frequence_paiement, 1)
        montant_echeance = int(montant_annuel / diviseur)

        # Déverrouillage temporaire pour réécriture
        self.entry_montant.config(state="normal")
        self.entry_montant.delete(0, tk.END)
        self.entry_montant.insert(0, str(montant_echeance))
        self.entry_montant.config(state="readonly")

    def valider(self):
        idx = self.combo_vehicule.current()
        if idx == -1:
            messagebox.showerror("Erreur", "Veuillez choisir un véhicule.")
            return

        vehicule_sel = self.vehicules_list[idx]
        vehicule_id = vehicule_sel['id']

        # 1. Récupération du montant total des frais sur 12 mois
        montant_total = get_montant_total_vehicule(vehicule_id)

        # Option A : Si vous souhaitez lire le montant saisi tout en autorisant un secours avec le montant total
        montant_val = self.entry_montant.get().strip()
        
        if montant_val.isdigit() and int(montant_val) > 0:
            montant_final = int(montant_val)
        else:
            # Si le champ est vide ou invalide, on prend le montant calculé
            montant_final = int(montant_total)

        # Vérification que le montant final est valide
        if montant_final <= 0:
            messagebox.showerror(
                "Erreur", 
                "Le montant doit être supérieur à 0 (aucun frais trouvé sur les 12 derniers mois)."
            )
            return

        try:
            # 2. Création du contrat avec le montant calculé / validé
            contrat_id, chemin_pdf = creer_nouveau_contrat(
                vehicule_id=vehicule_id,
                data_vehicule=vehicule_sel,
                montant=montant_final,
                tarif_formule=self.combo_tarif.get(),
                type_paiement=self.combo_paiement.get()
            )

            messagebox.showinfo(
                "Succès",
                f"Contrat N°{contrat_id} créé avec succès !\nMontant : {montant_final:,} MGA".replace(",", " ")
            )
            self.destroy()

        except Exception as e:
            print("--- ERREUR ENREGISTREMENT CONTRAT ---")
            traceback.print_exc()
            messagebox.showerror("Erreur", f"Échec de l'enregistrement :\n{e}")