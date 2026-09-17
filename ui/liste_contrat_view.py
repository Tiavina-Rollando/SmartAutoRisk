import os
import platform
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# Import du contrôleur des contrats
from controllers.contrat_controller import recuperer_liste_contrats, resilier_contrat


class ListeContratView(tk.Toplevel):
    """Vue dédiée à la liste et à la consultation des contrats enregistrés."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("SmartAutoRisk - Liste des Contrats")
        self.geometry("1100x650")
        self.configure(bg="#ecf0f1")

        # Rend la fenêtre modale
        self.transient(parent)
        self.grab_set()

        # Même système de cache que dans FacturesView
        self.contrats_cache = {}

        self.configurer_styles_ttk()
        self.creer_widgets()
        self.charger_donnees()

    def configurer_styles_ttk(self):
        """Configuration des styles graphiques alignés sur l'application."""
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Treeview",
            font=("Segoe UI", 11),
            rowheight=32,
            background="white",
            fieldbackground="white",
            foreground="#2c3e50"
        )
        style.map("Treeview", background=[("selected", "#3498db")], foreground=[("selected", "white")])
        
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 12, "bold"),
            background="#34495e",
            foreground="white",
            relief="flat"
        )
        style.map("Treeview.Heading", background=[("active", "#2c3e50")])

    def creer_widgets(self):
        header = tk.Frame(self, bg="#2c3e50", height=65)
        header.pack(fill="x")
        tk.Label(
            header, text="GESTION DES CONTRATS ENREGISTRÉS", 
            bg="#2c3e50", fg="white", font=("Segoe UI", 18, "bold")
        ).pack(pady=15)

        container = tk.Frame(self, bg="#ecf0f1")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        columns = ("id", "date", "client", "immat", "vehicule", "formule", "montant", "paiement")
        self.tree = ttk.Treeview(container, columns=columns, show="headings", height=10)

        self.tree.heading("id", text="N°")
        self.tree.heading("date", text="Date")
        self.tree.heading("client", text="Propriétaire")
        self.tree.heading("immat", text="Immatriculation")
        self.tree.heading("vehicule", text="Véhicule")
        self.tree.heading("formule", text="Formule")
        self.tree.heading("montant", text="Montant (MGA)")
        self.tree.heading("paiement", text="Paiement")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("date", width=110, anchor="center")
        self.tree.column("client", width=180, anchor="w")
        self.tree.column("immat", width=130, anchor="center")
        self.tree.column("vehicule", width=150, anchor="w")
        self.tree.column("formule", width=100, anchor="center")
        self.tree.column("montant", width=140, anchor="e")
        self.tree.column("paiement", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Action double-clic
        self.tree.bind("<Double-1>", lambda e: self.afficher_details_contrat())

        # Barre de boutons
        frame_btn = tk.Frame(self, bg="#ecf0f1")
        frame_btn.pack(fill="x", padx=20, pady=(0, 20))

        tk.Button(
            frame_btn, text="🔍 Infos Détaillées", command=self.afficher_details_contrat,
            bg="#2e6de6", fg="white", font=("Segoe UI", 12, "bold"), relief="flat", cursor="hand2", padx=18, pady=8
        ).pack(side="left", padx=(0, 10))

        # tk.Button(
        #     frame_btn, text="📄 Ouvrir Contrat PDF", command=self.action_ouvrir_pdf,
        #     bg="#27ae60", fg="white", font=("Segoe UI", 12, "bold"), relief="flat", cursor="hand2", padx=18, pady=8
        # ).pack(side="left")

        tk.Button(
            frame_btn, text="❌ Résilier Contrat", command=self.supprimer_contrat,
            bg="#e74c3c", fg="white", font=("Segoe UI", 12, "bold"), relief="flat", cursor="hand2", padx=18, pady=8
        ).pack(side="right")

    def charger_donnees(self):
        """Réinitialise le tableau et remplit self.contrats_cache exactement comme FacturesView."""
        self.tree.delete(*self.tree.get_children())
        self.contrats_cache.clear()

        contrats = recuperer_liste_contrats()

        for c in contrats:
            cid = c.get('contrat_id') or c.get('id')
            
            # Stockage dans le cache (clé unique)
            self.contrats_cache[cid] = c

            client_nom = f"{c.get('prop_nom', '')} {c.get('prop_prenom', '')}".strip() or "N/A"
            vehicule_str = f"{c.get('marque', '')} {c.get('modele', '')}".strip() or "N/A"
            montant = c.get('montant', 0)
            montant_str = f"{montant:,.0f}".replace(",", " ") if isinstance(montant, (int, float)) else str(montant)
            
            self.tree.insert("", tk.END, iid=cid, values=(
                cid,
                c.get('date_creation', ''),
                client_nom,
                c.get('immatriculation') or "N/A",
                vehicule_str,
                c.get('formule', ''),
                montant_str,
                c.get('type_paiement', '')
            ))

    def _get_selected_contrat(self):
        """Méthode utilitaire commune pour récupérer les données du cache via la ligne sélectionnée."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un contrat dans le tableau.", parent=self)
            return None, None

        item_id = selected[0]
        try:
            contrat_id = int(item_id)
        except ValueError:
            contrat_id = item_id

        contrat_data = self.contrats_cache.get(contrat_id) or self.contrats_cache.get(str(contrat_id), {})
        if not contrat_data:
            messagebox.showerror("Erreur", "Impossible de récupérer les détails de ce contrat depuis le cache.", parent=self)
            return None, None

        return contrat_id, contrat_data

    def action_ouvrir_pdf(self):
        """Ouvre le fichier PDF du contrat situé dans le dossier documents."""
        contrat_id, contrat_data = self._get_selected_contrat()
        if not contrat_data:
            return

        # Récupération du chemin dans le cache (compatible avec la clé 'path' ou 'pdf_path')
        pdf_path = contrat_data.get("path") or contrat_data.get("pdf_path") or ""

        if not pdf_path:
            # Construction de secours du chemin standard s'il n'est pas dans la BDD
            pdf_path = os.path.join("documents", f"contrat_{contrat_id}.pdf")

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
                f"Le fichier PDF du contrat est introuvable au chemin :\n{pdf_path_abs}",
                parent=self
            )

    def afficher_details_contrat(self, event=None):
        contrat_id, contrat_data = self._get_selected_contrat()
        if contrat_data:
            FenetreDetailsContrat(self, contrat_data)

    def supprimer_contrat(self):
        contrat_id, contrat_data = self._get_selected_contrat()
        if not contrat_data:
            return

        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir résilier le contrat N°{contrat_id} ?", parent=self):
            resilier_contrat(contrat_id)
            messagebox.showinfo("Succès", "Le contrat a été résilié.", parent=self)
            self.charger_donnees()


class FenetreDetailsContrat(tk.Toplevel):
    """Fenêtre Pop-up affichant les détails Client, Véhicule et Contrat."""
    def __init__(self, parent, data):
        super().__init__(parent)
        self.parent = parent
        self.data = data
        
        c_id = data.get('contrat_id') or data.get('id')
        self.title(f"Détails Contrat N°{c_id}")
        self.geometry("550x640")
        self.configure(bg="white")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()

        def fermer_dialog():
            self.grab_release()
            self.destroy()
            parent.grab_set()

        self.protocol("WM_DELETE_WINDOW", fermer_dialog)

        tk.Label(
            self, text=f"Fiche Contrat N°{c_id}", 
            font=("Segoe UI", 18, "bold"), bg="white", fg="#2c3e50"
        ).pack(pady=20)

        container = tk.Frame(self, bg="white", padx=30)
        container.pack(fill="both", expand=True)

        def ajouter_section(titre):
            lbl = tk.Label(container, text=titre, font=("Segoe UI", 13, "bold"), fg="#2e6de6", bg="white", anchor="w")
            lbl.pack(fill="x", pady=(14, 4))

        def ajouter_ligne(label, valeur):
            f = tk.Frame(container, bg="white")
            f.pack(fill="x", pady=3)
            tk.Label(f, text=label + " :", font=("Segoe UI", 11, "bold"), bg="white", width=20, anchor="w").pack(side="left")
            tk.Label(f, text=valeur, font=("Segoe UI", 11), bg="white", anchor="w").pack(side="left")

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
        
        montant = data.get('montant', 0)
        montant_str = f"{montant:,.0f}".replace(",", " ") if isinstance(montant, (int, float)) else str(montant)
        ajouter_ligne("Montant réglé", f"{montant_str} MGA")

        # Boutons du bas
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame, text="📄 Ouvrir PDF", command=self.ouvrir_pdf,
            bg="#27ae60", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", padx=15, pady=6, cursor="hand2"
        ).pack(side="left", padx=10)

        tk.Button(
            btn_frame, text="Fermer", command=fermer_dialog,
            bg="#2c3e50", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", padx=20, pady=6, cursor="hand2"
        ).pack(side="left", padx=10)

    def ouvrir_pdf(self):
        """Ouvre le fichier PDF depuis la modale de détails."""
        if hasattr(self.parent, 'action_ouvrir_pdf'):
            self.parent.action_ouvrir_pdf()
        else:
            pdf_path = self.data.get("path") or self.data.get("pdf_path") or ""
            if not pdf_path:
                c_id = self.data.get('contrat_id') or self.data.get('id')
                pdf_path = os.path.join("documents", f"contrat_{c_id}.pdf")

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