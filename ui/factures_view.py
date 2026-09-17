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
        self.title("SmartAutoRisk - Gestion des Factures & Paiements")
        self.geometry("1050x580")
        self.configure(bg="#ecf0f1")
        
        # Fenêtre modale au premier plan
        self.transient(parent)
        self.grab_set()

        self.vehicule_id = vehicule_id
        self.contrat = None
        self.factures_cache = {}

        self.configurer_styles_ttk()
        self.setup_ui()
        self.charger_donnees()

    def configurer_styles_ttk(self):
        """Configuration des styles graphiques pour aligner le design sur l'application."""
        style = ttk.Style(self)
        style.theme_use("clam")

        # Configuration des lignes du tableau
        style.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=32,
            background="white",
            fieldbackground="white",
            foreground="#2c3e50"
        )
        style.map("Treeview", background=[("selected", "#3498db")], foreground=[("selected", "white")])

        # En-têtes du tableau
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 11, "bold"),
            background="#34495e",
            foreground="white",
            relief="flat"
        )
        style.map("Treeview.Heading", background=[("active", "#2c3e50")])

    def setup_ui(self):
        # --- En-tête principal ---
        header = tk.Frame(self, bg="#2c3e50", height=60)
        header.pack(fill="x")

        self.lbl_title = tk.Label(
            header, 
            text="HISTORIQUE DES FACTURES & PAIEMENTS", 
            font=("Segoe UI", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        self.lbl_title.pack(side=tk.LEFT, padx=20, pady=12)

        self.lbl_contrat_info = tk.Label(
            header, 
            text="", 
            font=("Segoe UI", 11, "italic"),
            bg="#2c3e50",
            fg="#bdc3c7"
        )
        self.lbl_contrat_info.pack(side=tk.RIGHT, padx=20, pady=12)

        # --- Conteneur du tableau ---
        table_frame = tk.Frame(self, bg="#ecf0f1")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        columns = ("id", "date", "plage_deb", "plage_fin", "frais", "statut", "commentaire")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="N° Facture")
        self.tree.heading("date", text="Date Paiement")
        self.tree.heading("plage_deb", text="Début Couverture")
        self.tree.heading("plage_fin", text="Fin Couverture")
        self.tree.heading("frais", text="Montant (MGA)")
        self.tree.heading("statut", text="Statut")
        self.tree.heading("commentaire", text="Commentaire")

        self.tree.column("id", width=110, anchor=tk.CENTER)
        self.tree.column("date", width=110, anchor=tk.CENTER)
        self.tree.column("plage_deb", width=120, anchor=tk.CENTER)
        self.tree.column("plage_fin", width=120, anchor=tk.CENTER)
        self.tree.column("frais", width=130, anchor=tk.E)
        self.tree.column("statut", width=100, anchor=tk.CENTER)
        self.tree.column("commentaire", width=250, anchor=tk.W)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Action double-clic
        self.tree.bind("<Double-1>", lambda e: self.action_afficher_details_facture())

        # --- Barre d'actions (Boutons) ---
        btn_frame = tk.Frame(self, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Button(
            btn_frame, 
            text="➕ Enregistrer un Paiement", 
            command=self.action_ouvrir_dialogue_paiement,
            bg="#27ae60", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2", padx=14, pady=6
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            btn_frame,
            text="🔍 Infos Détaillées",
            command=self.action_afficher_details_facture,
            bg="#2e6de6", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2", padx=14, pady=6
        ).pack(side=tk.LEFT, padx=(0, 10))

        # tk.Button(
        #     btn_frame, 
        #     text="📄 Ouvrir Facture PDF", 
        #     command=self.action_ouvrir_pdf,
        #     bg="#8e44ad", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2", padx=14, pady=6
        # ).pack(side=tk.LEFT)

        tk.Button(
            btn_frame, 
            text="Fermer", 
            command=self.destroy,
            bg="#7f8c8d", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2", padx=18, pady=6
        ).pack(side=tk.RIGHT)

    def charger_donnees(self):
        """Charge le contrat actif du véhicule et l'historique des factures."""
        self.tree.delete(*self.tree.get_children())
        self.factures_cache.clear()

        # 1. Récupération du contrat
        self.contrat = get_contrat_by_vehicule(self.vehicule_id)

        if not self.contrat:
            self.lbl_contrat_info.config(text="⚠️ Aucun contrat actif")
            messagebox.showwarning(
                "Avertissement", 
                "Ce véhicule n'a pas encore de contrat actif enregistré.", 
                parent=self
            )
            return

        contrat_id = self.contrat.get("id")
        type_paiement = self.contrat.get("type_paiement", "").capitalize()
        self.lbl_contrat_info.config(text=f"Contrat N°{contrat_id} • {type_paiement}")

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

    def action_afficher_details_facture(self):
        """Affiche les détails complets de la facture sélectionnée dans une modale stylisée."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une facture dans le tableau.", parent=self)
            return

        # Récupération sécurisée de l'ID (gestion int/str)
        item_id = selected[0]
        try:
            facture_id = int(item_id)
        except ValueError:
            facture_id = item_id

        # Recherche dans le cache (compatible clé int ou str)
        facture_data = self.factures_cache.get(str(facture_id)) or self.factures_cache.get(facture_id, {})
        if not facture_data:
            messagebox.showerror("Erreur", "Impossible de récupérer les détails de cette facture.", parent=self)
            return

        # Création de la fenêtre modale
        dialog = tk.Toplevel(self)
        fac_title = f"FAC-{facture_id:05d}" if isinstance(facture_id, int) else f"FAC-{facture_id}"
        dialog.title(f"Fiche Facture {fac_title}")
        dialog.geometry("500x500")
        dialog.configure(bg="#f8f9fa")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Fonction de fermeture propre libérant le grab
        def fermer_dialog():
            dialog.grab_release()
            dialog.destroy()
            self.grab_set()

        dialog.protocol("WM_DELETE_WINDOW", fermer_dialog)

        # En-tête avec bandeau sombre
        header_frame = tk.Frame(dialog, bg="#2c3e50", height=50)
        header_frame.pack(fill=tk.X)
        tk.Label(
            header_frame, 
            text=f"Détails Facture N° {fac_title}", 
            font=("Segoe UI", 14, "bold"), 
            bg="#2c3e50", 
            fg="white"
        ).pack(pady=12)

        # Conteneur des informations
        container = tk.Frame(dialog, bg="white", padx=25, pady=15, relief="solid", bd=1)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        def add_row(parent, label, value, fg_color="#2c3e50"):
            row = tk.Frame(parent, bg="white")
            row.pack(fill=tk.X, pady=4)
            tk.Label(
                row, text=label + " :", font=("Segoe UI", 10, "bold"), 
                bg="white", width=18, anchor="w", fg="#34495e"
            ).pack(side=tk.LEFT)
            tk.Label(
                row, text=str(value), font=("Segoe UI", 10), 
                bg="white", anchor="w", wraplength=240, justify="left", fg=fg_color
            ).pack(side=tk.LEFT)

        # Préparation des valeurs
        frais = facture_data.get("frais", 0)
        frais_str = f"{frais:,.0f} MGA".replace(",", " ") if isinstance(frais, (int, float)) else f"{frais} MGA"
        
        statut_code = facture_data.get("statut", 0)
        statut_txt = "Payé" if statut_code == 1 else "En attente"
        statut_color = "#27ae60" if statut_code == 1 else "#e67e22"

        pdf_path = (
            facture_data.get("path") 
            or facture_data.get("pdf_path") 
            or facture_data.get("fichier_pdf") 
            or "Non spécifié"
        )
        contrat_id = facture_data.get("contrat_id") or (self.contrat.get("id") if self.contrat else "N/A")

        # Insertion des lignes d'information
        add_row(container, "N° Contrat", contrat_id)
        add_row(container, "Date de paiement", facture_data.get("date", "N/A"))
        add_row(container, "Début couverture", facture_data.get("plage_deb", "N/A"))
        add_row(container, "Fin couverture", facture_data.get("plage_fin", "N/A"))
        add_row(container, "Montant réglé", frais_str, fg_color="#2980b9")
        add_row(container, "Statut", statut_txt, fg_color=statut_color)
        add_row(container, "Commentaire", facture_data.get("commentaire") or "Aucun")
        add_row(container, "Fichier PDF", pdf_path)

        # Barre d'actions en bas de la modale
        btn_frame = tk.Frame(dialog, bg="#f8f9fa")
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        # Bouton Ouvrir PDF
        def action_pdf_locale():
            if hasattr(self, 'action_ouvrir_pdf'):
                self.action_ouvrir_pdf()
            elif hasattr(self, 'ouvrir_pdf'):
                self.ouvrir_pdf()

        btn_pdf = tk.Button(
            btn_frame, text="📄 Ouvrir PDF", command=action_pdf_locale,
            bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), 
            relief="flat", padx=15, pady=6, cursor="hand2"
        )
        btn_pdf.pack(side=tk.LEFT)

        # Bouton Fermer
        btn_fermer = tk.Button(
            btn_frame, text="Fermer", command=fermer_dialog,
            bg="#7f8c8d", fg="white", font=("Segoe UI", 10, "bold"), 
            relief="flat", padx=20, pady=6, cursor="hand2"
        )
        btn_fermer.pack(side=tk.RIGHT)
        
    def ouvrir_pdf(self):
        """Ouvre le fichier PDF associé à la facture sélectionnée."""
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une facture dans le tableau.", parent=self)
            return

        try:
            facture_id = int(selected[0])
        except ValueError:
            facture_id = selected[0]

        facture_data = self.factures_cache.get(facture_id, {})
        pdf_path = facture_data.get("path") or facture_data.get("pdf_path") or ""

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
                f"Le fichier PDF est introuvable au chemin :\n{pdf_path_abs}", 
                parent=self
            )

    def action_ouvrir_dialogue_paiement(self):
        """Ouvre une modale élégante pour la saisie d'un paiement."""
        if not self.contrat:
            messagebox.showerror("Erreur", "Impossible d'ajouter un paiement : aucun contrat associé.", parent=self)
            return

        dialog = tk.Toplevel(self)
        dialog.title("Saisie d'un nouveau paiement")
        dialog.geometry("420x300")
        dialog.configure(bg="white")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(
            dialog, text="Nouveau Paiement", 
            font=("Segoe UI", 14, "bold"), bg="white", fg="#2c3e50"
        ).pack(pady=(15, 10))

        form_frame = tk.Frame(dialog, bg="white", padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(form_frame, text="Date début couverture (AAAA-MM-JJ) :", font=("Segoe UI", 10, "bold"), bg="white", anchor="w").pack(fill=tk.X, pady=(5, 2))
        ent_plage_deb = ttk.Entry(form_frame, font=("Segoe UI", 10))
        ent_plage_deb.insert(0, datetime.now().strftime("%Y-%m-%d"))
        ent_plage_deb.pack(fill=tk.X, pady=(0, 8))

        tk.Label(form_frame, text="Commentaire / Notes :", font=("Segoe UI", 10, "bold"), bg="white", anchor="w").pack(fill=tk.X, pady=(5, 2))
        ent_comment = ttk.Entry(form_frame, font=("Segoe UI", 10))
        ent_comment.insert(0, "Paiement effectué")
        ent_comment.pack(fill=tk.X, pady=(0, 8))

        type_p = self.contrat.get("type_paiement", "annuel").capitalize()
        lbl_info = tk.Label(
            form_frame, 
            text=f"ℹ️ Le montant et la date de fin seront calculés\nautomatiquement selon le mode de paiement ({type_p}).", 
            fg="#7f8c8d", bg="white", font=("Segoe UI", 9, "italic"), justify="left"
        )
        lbl_info.pack(anchor="w", pady=(0, 10))

        def valider_paiement():
            plage_deb_val = ent_plage_deb.get().strip()
            comment_val = ent_comment.get().strip()

            if not plage_deb_val:
                messagebox.showerror("Erreur", "Veuillez remplir la date de début.", parent=dialog)
                return

            try:
                datetime.strptime(plage_deb_val, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Erreur", "Le format de la date doit être AAAA-MM-JJ.", parent=dialog)
                return

            try:
                creer_nouveau_paiement(
                    contrat_id=self.contrat["id"],
                    plage_deb=plage_deb_val,
                    commentaire=comment_val
                )
                messagebox.showinfo("Succès", "Paiement enregistré et facture PDF générée avec succès !", parent=dialog)
                dialog.destroy()
                self.charger_donnees()

            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue lors du paiement :\n{e}", parent=dialog)

        tk.Button(
            dialog, text="Valider & Générer Facture", command=valider_paiement,
            bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=15, pady=6, cursor="hand2"
        ).pack(pady=(0, 15))

    def action_ouvrir_pdf(self):
        """Ouvre le fichier PDF associé à la facture sélectionnée."""
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une facture dans le tableau.", parent=self)
            return

        try:
            facture_id = int(selected[0])
        except ValueError:
            facture_id = selected[0]

        facture_data = self.factures_cache.get(facture_id, {})
        pdf_path = facture_data.get("path") or facture_data.get("pdf_path") or ""

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
                f"Le fichier PDF est introuvable au chemin :\n{pdf_path_abs}", 
                parent=self
            )