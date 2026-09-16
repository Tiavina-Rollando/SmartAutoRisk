import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry  # Calendrier interactif

# Import des contrôleurs
import controllers.accident_controller as acc_ctrl
import controllers.vehicule_controller as veh_ctrl


class Accidents(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#f5f6fa")

        self.vehicules_dict = {}  # Mapping "Immatriculation (Marque)" -> ID_vehicule

        # ================= STYLE =================
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), background="#f5f6fa", foreground="#2c3e50")
        style.configure("Result.TLabel", font=("Segoe UI", 14, "bold"), foreground="#2c3e50")

        # Style des en-têtes du tableau (Treeview)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#2c3e50", foreground="white")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)

        # ================= HEADER =================
        header = tk.Frame(self, bg="#2c3e50", height=60)
        header.pack(fill="x")

        tk.Label(
            header,
            text="SMART AUTORISK - ACCIDENTS",
            bg="#2c3e50",
            fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=15)

        # ================= CONTENU PRINCIPAL =================
        content_frame = tk.Frame(self, bg="#f5f6fa")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ---------------- FORMULAIRE ACCIDENT (GAUCHE) ----------------
        form_card = ttk.Frame(content_frame, style="Card.TFrame", padding=15)
        form_card.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(form_card, text="Déclarer un Accident", font=("Segoe UI", 13, "bold"), background="white", foreground="#2c3e50").pack(anchor="w", pady=(0, 15))

        # Champ : Véhicule (Combobox issu de la BDD)
        tk.Label(form_card, text="Véhicule concerné :", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(2, 0))
        self.combo_vehicule = ttk.Combobox(form_card, width=30, state="readonly")
        self.combo_vehicule.pack(fill="x", pady=(0, 8))

        # Champ : Date de l'accident (Sélecteur de Date)
        tk.Label(form_card, text="Date de l'accident :", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(2, 0))
        self.date_picker = DateEntry(
            form_card,
            width=28,
            background='#2c3e50',
            foreground='white',
            bordercolor='#2c3e50',
            headersbackground='#34495e',
            headersforeground='white',
            date_pattern='yyyy-mm-dd', # Format compatible MySQL
            state="readonly" # Empêche la saisie manuelle
        )
        self.date_picker.pack(fill="x", pady=(0, 8))

        # Champ : Lieu
        tk.Label(form_card, text="Lieu :", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(2, 0))
        self.entry_lieu = ttk.Entry(form_card, width=30)
        self.entry_lieu.pack(fill="x", pady=(0, 8))

        # Champ : Type (ENUM: matériel, physique)
        tk.Label(form_card, text="Type d'accident :", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(2, 0))
        self.combo_type = ttk.Combobox(form_card, values=["matériel", "physique"], state="readonly")
        self.combo_type.pack(fill="x", pady=(0, 8))
        self.combo_type.current(0)

        # Champ : Degât / Gravité (ENUM: faible, moyen, élevé)
        tk.Label(form_card, text="Degât :", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(2, 0))
        self.combo_degat = ttk.Combobox(form_card, values=["faible", "moyen", "élévé"], state="readonly")
        self.combo_degat.pack(fill="x", pady=(0, 8))
        self.combo_degat.current(0)

        # Champ : Responsabilité (TinyInt: 0 ou 1)
        tk.Label(form_card, text="Responsabilité (1=Oui, 0=Non) :", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(2, 0))
        self.combo_resp = ttk.Combobox(form_card, values=["0", "1"], state="readonly")
        self.combo_resp.pack(fill="x", pady=(0, 8))
        self.combo_resp.current(0)

        # Champ : Rôle (ENUM: fautif, victime, tiers)
        tk.Label(form_card, text="Rôle du conducteur :", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(2, 0))
        self.combo_role = ttk.Combobox(form_card, values=["fautif", "victime", "tiers"], state="readonly")
        self.combo_role.pack(fill="x", pady=(0, 8))
        self.combo_role.current(0)

        # Champ : Valeur des dégâts (BigInt)
        tk.Label(form_card, text="Valeur dégâts (Ar) :", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(2, 0))
        self.entry_valeur = ttk.Entry(form_card, width=30)
        self.entry_valeur.pack(fill="x", pady=(0, 12))

        # Boutons d'action
        btn_frame = tk.Frame(form_card, bg="white")
        btn_frame.pack(fill="x", pady=5)

        btn_save = tk.Button(
            btn_frame,
            text="Enregistrer",
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.enregistrer_accident
        )
        btn_save.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_reset = tk.Button(
            btn_frame,
            text="Vider",
            bg="#7f8c8d",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.reinitialiser_formulaire
        )
        btn_reset.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # ---------------- TABLEAU HISTORIQUE (DROITE) ----------------
        table_card = ttk.Frame(content_frame, style="Card.TFrame", padding=15)
        table_card.pack(side="right", fill="both", expand=True)

        ttk.Label(table_card, text="Historique des Sinistres (BDD)", font=("Segoe UI", 13, "bold"), background="white", foreground="#2c3e50").pack(anchor="w", pady=(0, 15))

        # Configuration du Treeview
        columns = ("id", "date", "immat", "lieu", "type", "degat", "resp", "role", "valeur")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", height=15)

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("immat", text="Immatriculation")
        self.tree.heading("lieu", text="Lieu")
        self.tree.heading("type", text="Type")
        self.tree.heading("degat", text="Dégât")
        self.tree.heading("resp", text="Resp.")
        self.tree.heading("role", text="Rôle")
        self.tree.heading("valeur", text="Valeur (Ar)")

        self.tree.column("id", width=30, anchor="center")
        self.tree.column("date", width=90, anchor="center")
        self.tree.column("immat", width=90, anchor="center")
        self.tree.column("lieu", width=100)
        self.tree.column("type", width=90, anchor="center")
        self.tree.column("degat", width=70, anchor="center")
        self.tree.column("resp", width=50, anchor="center")
        self.tree.column("role", width=70, anchor="center")
        self.tree.column("valeur", width=90, anchor="e")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Initialisation des données
        self.charger_liste_vehicules()
        self.charger_historique()

    # ================= CHARGEMENT DES DONNÉES BDD =================
    def charger_liste_vehicules(self):
        try:
            vehicules = veh_ctrl.charger_vehicules() if hasattr(veh_ctrl, 'charger_vehicules') else []
            self.vehicules_dict = {}
            list_display = []

            for v in vehicules:
                v_id = v.get('id') if isinstance(v, dict) else v[0]
                immat = v.get('immatriculation') if isinstance(v, dict) else v[1]
                marque = v.get('marque', '') if isinstance(v, dict) else (v[2] if len(v) > 2 else '')

                display_text = f"{immat} - {marque}".strip(" -")
                self.vehicules_dict[display_text] = v_id
                list_display.append(display_text)

            self.combo_vehicule['values'] = list_display
            if list_display:
                self.combo_vehicule.current(0)
        except Exception as e:
            print(f"Erreur chargement véhicules : {e}")

    def charger_historique(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            accidents = acc_ctrl.charger_accidents_vehicules()
            for row in accidents:
                self.tree.insert("", "end", values=(
                    row.get('id'),
                    row.get('date'),
                    row.get('immatriculation'),
                    row.get('lieu'),
                    row.get('type_accident'),
                    row.get('degat'),
                    row.get('responsabilite'),
                    row.get('role'),
                    f"{row.get('valeur'):,}" if row.get('valeur') else 0
                ))
        except Exception as e:
            print(f"Erreur chargement historique accidents : {e}")

    # ================= ACTIONS ET LOGIQUE METIER =================
    def enregistrer_accident(self):
        selected_veh = self.combo_vehicule.get()
        date_acc = self.date_picker.get_date().strftime('%Y-%m-%d')  # Récupération sécurisée
        lieu = self.entry_lieu.get().strip()
        type_acc = self.combo_type.get()
        degat = self.combo_degat.get()
        resp = int(self.combo_resp.get())
        role = self.combo_role.get()
        valeur_str = self.entry_valeur.get().strip()

        if not selected_veh or not lieu:
            messagebox.showwarning("Champs obligatoires", "Veuillez renseigner le véhicule et le lieu de l'accident.")
            return

        vehicule_id = self.vehicules_dict.get(selected_veh)
        if not vehicule_id:
            messagebox.showerror("Erreur", "Véhicule sélectionné non valide.")
            return

        try:
            valeur = int(valeur_str) if valeur_str else 0
        except ValueError:
            messagebox.showwarning("Erreur Saisie", "La valeur des dégâts doit être un nombre entier.")
            return

        try:
            acc_ctrl.enregistrer_accident_complet(
                date_acc=date_acc,
                lieu=lieu,
                type_acc=type_acc,
                vehicule_id=vehicule_id,
                degat=degat,
                responsabilite=resp,
                role=role,
                valeur=valeur
            )

            messagebox.showinfo("Succès", "L'accident a été enregistré en BDD avec succès.")
            self.reinitialiser_formulaire()
            self.charger_historique()

        except Exception as e:
            messagebox.showerror("Erreur BDD", f"Erreur lors de l'enregistrement : {e}")

    def reinitialiser_formulaire(self):
        self.entry_lieu.delete(0, tk.END)
        self.entry_valeur.delete(0, tk.END)
        self.combo_type.current(0)
        self.combo_degat.current(0)
        self.combo_resp.current(0)
        self.combo_role.current(0)