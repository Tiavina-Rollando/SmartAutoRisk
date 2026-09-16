import os
import platform
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Imports des contrôleurs et modèles
from controllers.factures_controller import (
    creer_nouveau_paiement, 
    lister_factures_contrat
)
from models.contrat_model import get_contrat_by_vehicule


class FacturesView(tk.Toplevel):
    def __init__(self, parent, vehicule_id):
        super().__init__(parent)
        self.title("Gestion des Factures & Paiements")
        self.geometry("900x500")
        self.resizable(True, True)
        
        # Pour forcer la fenêtre au premier plan
        self.transient(parent)
        self.grab_set()

        self.vehicule_id = vehicule_id
        self.contrat = None
        self.factures_cache = {}

        self.setup_ui()
        self.charger_donnees()

    def setup_ui(self):
        # --- En-tête ---
        header_frame = ttk.Frame(self, padding=10)
        header_frame.pack(fill=tk.X)

        self.lbl_title = ttk.Label(
            header_frame, 
            text="Historique des Factures & Paiements", 
            font=("Helvetica", 14, "bold")
        )
        self.lbl_title.pack(side=tk.LEFT)

        self.lbl_contrat_info = ttk.Label(
            header_frame, 
            text="", 
            font=("Helvetica", 10, "italic")
        )
        self.lbl_contrat_info.pack(side=tk.RIGHT)

        # --- Tableau (Treeview) ---
        table_frame = ttk.Frame(self, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "date", "plage_deb", "plage_fin", "frais", "statut", "commentaire")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="N° Facture")
        self.tree.heading("date", text="Date Paiement")
        self.tree.heading("plage_deb", text="Début Couverture")
        self.tree.heading("plage_fin", text="Fin Couverture")
        self.tree.heading("frais", text="Montant (Ar)")
        self.tree.heading("statut", text="Statut")
        self.tree.heading("commentaire", text="Commentaire")

        self.tree.column("id", width=80, anchor=tk.CENTER)
        self.tree.column("date", width=110, anchor=tk.CENTER)
        self.tree.column("plage_deb", width=120, anchor=tk.CENTER)
        self.tree.column("plage_fin", width=120, anchor=tk.CENTER)
        self.tree.column("frais", width=110, anchor=tk.E)
        self.tree.column("statut", width=90, anchor=tk.CENTER)
        self.tree.column("commentaire", width=200, anchor=tk.W)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Barre d'actions (Boutons) ---
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=tk.X)

        btn_nouveau = ttk.Button(
            btn_frame, 
            text="➕ Enregistrer un Paiement", 
            command=self.action_ouvrir_dialogue_paiement
        )
        btn_nouveau.pack(side=tk.LEFT, padx=5)

        btn_pdf = ttk.Button(
            btn_frame, 
            text="📄 Ouvrir Facture PDF", 
            command=self.action_ouvrir_pdf
        )
        btn_pdf.pack(side=tk.LEFT, padx=5)

        btn_fermer = ttk.Button(
            btn_frame, 
            text="Fermer", 
            command=self.destroy
        )
        btn_fermer.pack(side=tk.RIGHT, padx=5)

    def charger_donnees(self):
        """Charge le contrat actif du véhicule et l'historique des factures."""
        self.tree.delete(*self.tree.get_children())
        self.factures_cache.clear()

        # 1. Récupération du contrat
        self.contrat = get_contrat_by_vehicule(self.vehicule_id)

        if not self.contrat:
            self.lbl_contrat_info.config(text="⚠️ Aucun contrat actif associé à ce véhicule.")
            messagebox.showwarning(
                "Avertissement", 
                "Ce véhicule n'a pas encore de contrat actif enregistré.", 
                parent=self
            )
            return

        contrat_id = self.contrat.get("id")
        type_paiement = self.contrat.get("type_paiement", "").capitalize()
        self.lbl_contrat_info.config(text=f"Contrat N°{contrat_id} ({type_paiement})")

        # 2. Récupération des factures
        factures = lister_factures_contrat(contrat_id)

        for f in factures:
            fid = f.get("id")
            self.factures_cache[fid] = f

            date_pay = f.get("date", "")
            plage_deb = f.get("plage_deb", "")
            plage_fin = f.get("plage_fin", "")
            frais = f.get("frais", 0)
            statut_code = f.get("statut", 0)
            statut_txt = "Payé" if statut_code == 1 else "En attente"
            commentaire = f.get("commentaire", "")

            # Formattage du montant
            frais_str = f"{frais:,.0f}".replace(",", " ") if isinstance(frais, (int, float)) else str(frais)

            self.tree.insert("", tk.END, iid=fid, values=(
                f"FAC-{fid:05d}",
                date_pay,
                plage_deb,
                plage_fin,
                frais_str,
                statut_txt,
                commentaire
            ))

    def action_ouvrir_dialogue_paiement(self):
        """Ouvre une modale pour saisir un nouveau paiement."""
        if not self.contrat:
            messagebox.showerror("Erreur", "Impossible d'ajouter un paiement : aucun contrat associé.", parent=self)
            return

        # Création d'une fenêtre de dialogue
        dialog = tk.Toplevel(self)
        dialog.title("Saisie d'un nouveau paiement")
        dialog.geometry("400x260")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        padding = {'padx': 10, 'pady': 5}

        # Date de début de couverture (par défaut aujourd'hui)
        ttk.Label(dialog, text="Date début couverture (AAAA-MM-JJ) :").pack(anchor=tk.W, **padding)
        ent_plage_deb = ttk.Entry(dialog, width=30)
        ent_plage_deb.insert(0, datetime.now().strftime("%Y-%m-%d"))
        ent_plage_deb.pack(anchor=tk.W, **padding)

        # Commentaire
        ttk.Label(dialog, text="Commentaire / Notes :").pack(anchor=tk.W, **padding)
        ent_comment = ttk.Entry(dialog, width=30)
        ent_comment.insert(0, "Paiement effectue")
        ent_comment.pack(anchor=tk.W, **padding)

        # Indication sur le calcul automatique de la date de fin et du montant
        type_p = self.contrat.get("type_paiement", "annuel").capitalize()
        lbl_info = ttk.Label(
            dialog, 
            text=f"ℹ️ Le montant de la tranche et la date de fin de couverture\nseront calculés automatiquement ({type_p}).", 
            foreground="gray",
            font=("Helvetica", 8, "italic")
        )
        lbl_info.pack(anchor=tk.W, **padding)

        # Action de validation
        def valider_paiement():
            plage_deb_val = ent_plage_deb.get().strip()
            comment_val = ent_comment.get().strip()

            if not plage_deb_val:
                messagebox.showerror("Erreur", "Veuillez remplir la date de début.", parent=dialog)
                return

            # Validation du format date
            try:
                datetime.strptime(plage_deb_val, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Erreur", "Le format de la date doit être AAAA-MM-JJ (ex: 2026-03-31).", parent=dialog)
                return

            try:
                # Appel au contrôleur sans le montant (calculé côté contrôleur)
                creer_nouveau_paiement(
                    contrat_id=self.contrat["id"],
                    plage_deb=plage_deb_val,
                    commentaire=comment_val
                )
                messagebox.showinfo("Succès", "Paiement enregistré et facture PDF générée avec succès !", parent=dialog)
                dialog.destroy()
                
                # Rafraîchir la liste dans l'UI
                self.charger_donnees()

            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue lors du paiement :\n{e}", parent=dialog)

        btn_valider = ttk.Button(dialog, text="Valider & Générer Facture", command=valider_paiement)
        btn_valider.pack(pady=15)

    def action_ouvrir_pdf(self):
        """Ouvre le fichier PDF associé à la facture sélectionnée."""
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner une facture dans le tableau.", parent=self)
            return

        try:
            facture_id = int(selected[0])
        except ValueError:
            facture_id = selected[0]

        facture_data = self.factures_cache.get(facture_id, {})
        pdf_path = facture_data.get("path", "")

        if not pdf_path:
            messagebox.showerror("Erreur", "Aucun fichier PDF n'est enregistré pour cette facture.", parent=self)
            return

        pdf_path_abs = os.path.abspath(pdf_path)

        if os.path.exists(pdf_path_abs):
            try:
                if platform.system() == "Windows":
                    os.startfile(pdf_path_abs)
                elif platform.system() == "Darwin":
                    subprocess.run(["open", pdf_path_abs])
                else:
                    subprocess.run(["xdg-open", pdf_path_abs])
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}", parent=self)
        else:
            messagebox.showerror(
                "Fichier introuvable", 
                f"Le fichier PDF est introuvable sur le disque au chemin :\n{pdf_path_abs}", 
                parent=self
            )