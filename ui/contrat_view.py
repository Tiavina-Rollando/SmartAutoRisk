import traceback
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
from controllers.contrat_controller import (
    creer_nouveau_contrat,
    recuperer_liste_vehicules
)


class ContratView(tk.Toplevel):
    """Fenêtre de Souscription d'un Contrat."""
    def __init__(self, parent, vehicule_id=None, data_vehicule=None):
        super().__init__(parent)
        self.vehicule_id = vehicule_id
        self.data_vehicule = data_vehicule or {}

        self.title("Souscription de Contrat")
        self.geometry("480x550")
        self.configure(bg="#f4f6f9")
        self.resizable(False, False)

        self.vehicules_list = recuperer_liste_vehicules()
        self.creer_widgets()

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
        label_titre = tk.Label(
            self, text="Nouveau Contrat d'Assurance", 
            font=("Segoe UI", 14, "bold"), bg="#f4f6f9", fg="#2e6de6"
        )
        label_titre.pack(pady=15)

        frame_form = tk.Frame(self, bg="#f4f6f9", padx=25)
        frame_form.pack(fill="both", expand=True)

        # 1. Véhicule
        tk.Label(frame_form, text="Véhicule :", font=("Segoe UI", 10, "bold"), bg="#f4f6f9", anchor="w").pack(fill="x", pady=(5, 2))
        options_vehicules = [f"{v['id']} - {v['immatriculation']} ({v['marque']} {v['modele']})" for v in self.vehicules_list]
        
        self.combo_vehicule = ttk.Combobox(frame_form, values=options_vehicules, state="readonly", font=("Segoe UI", 10))
        self.combo_vehicule.pack(fill="x", ipady=3)
        self.combo_vehicule.bind("<<ComboboxSelected>>", self.recalculer_montant_tarif)

        # 2. Formule / Tarif
        tk.Label(frame_form, text="Tarif (Formule) :", font=("Segoe UI", 10, "bold"), bg="#f4f6f9", anchor="w").pack(fill="x", pady=(10, 2))
        self.combo_tarif = ttk.Combobox(frame_form, values=["simple", "prenium"], state="readonly", font=("Segoe UI", 10))
        self.combo_tarif.set("prenium" if self.data_vehicule.get('tarif') == "prenium" else "simple")
        self.combo_tarif.pack(fill="x", ipady=3)
        self.combo_tarif.bind("<<ComboboxSelected>>", self.recalculer_montant_tarif)

        # 3. Type de paiement (BIND AJOUTÉ ICI)
        tk.Label(frame_form, text="Type de paiement :", font=("Segoe UI", 10, "bold"), bg="#f4f6f9", anchor="w").pack(fill="x", pady=(10, 2))
        self.combo_paiement = ttk.Combobox(frame_form, values=["Annuel", "Semestriel", "Trimestriel", "Mensuel"], state="readonly", font=("Segoe UI", 10))
        self.combo_paiement.set("Annuel")
        self.combo_paiement.pack(fill="x", ipady=3)
        self.combo_paiement.bind("<<ComboboxSelected>>", self.recalculer_montant_tarif)

        # 4. Montant Calculé
        tk.Label(frame_form, text="Montant de l'échéance (MGA) :", font=("Segoe UI", 10, "bold"), bg="#f4f6f9", fg="#27ae60", anchor="w").pack(fill="x", pady=(10, 2))
        self.entry_montant = tk.Entry(frame_form, font=("Segoe UI", 11, "bold"), fg="#27ae60")
        self.entry_montant.pack(fill="x", ipady=4)

        if self.vehicule_id:
            for idx, v in enumerate(self.vehicules_list):
                if str(v['id']) == str(self.vehicule_id):
                    self.combo_vehicule.current(idx)
                    break
        elif options_vehicules:
            self.combo_vehicule.current(0)

        btn_valider = tk.Button(
            self, text="Enregistrer le contrat", command=self.valider,
            bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2"
        )
        btn_valider.pack(pady=20, ipadx=10, ipady=6)

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

        self.entry_montant.delete(0, tk.END)
        self.entry_montant.insert(0, str(montant_echeance))

    def valider(self):
        idx = self.combo_vehicule.current()
        if idx == -1:
            messagebox.showerror("Erreur", "Veuillez choisir un véhicule.")
            return

        vehicule_sel = self.vehicules_list[idx]
        montant_val = self.entry_montant.get().strip()

        if not montant_val.isdigit() or int(montant_val) <= 0:
            messagebox.showerror("Erreur", "Veuillez entrer un montant valide.")
            return

        try:
            contrat_id, chemin_pdf = creer_nouveau_contrat(
                vehicule_id=vehicule_sel['id'],
                data_vehicule=vehicule_sel,
                montant=int(montant_val),
                tarif_formule=self.combo_tarif.get(),
                type_paiement=self.combo_paiement.get()
            )

            messagebox.showinfo("Succès", f"Contrat N°{contrat_id} créé avec succès !\nMontant : {montant_val} MGA")
            self.destroy()

        except Exception as e:
            # Affiche l'erreur détaillée dans la console du terminal pour le débogage
            print("--- ERREUR ENREGISTREMENT CONTRAT ---")
            traceback.print_exc()
            messagebox.showerror("Erreur", f"Échec de l'enregistrement :\n{e}")