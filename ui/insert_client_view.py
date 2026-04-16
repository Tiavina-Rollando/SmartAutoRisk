import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from controllers.vehicule_controller import ajouter_vehicule_db
from controllers.proprietaire_controller import ajouter_client, charger_clients
from RNA_PROFIL.rna_profil import NeuralNetwork as ProfilNN
from RNA_RISK.rna_risk import NeuralNetwork as RiskNN
from RNA_RATE.rna_rate import NeuralNetwork as FeeNN
from services.recuperation import get_all_seasons, get_vehicle, get_owner, get_niveau_risque
from services.enregistrement import insert_profil, insert_risk, insert_frais


# ================= MODELS =================
profil_model = ProfilNN(4, 5, 3)
profil_model.load_model("models/profil_model.json")

risque_model = RiskNN(8, 10, 3)
risque_model.load_model("models/risk_model.json")

frais_model = FeeNN(6, 6)
frais_model.load_model("models/rate_model.json")


class AjoutVehiculeView(tk.Frame):

    def __init__(self, parent, refresh_callback=None):
        self.refresh_callback = refresh_callback
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        # ================= WINDOW =================
        self.parent = parent
        self.parent.geometry("950x550")
        self.parent.minsize(950, 550)

        tk.Label(self, text="Ajout Véhicule", font=("Arial", 18, "bold")).pack(pady=10)

        # ================= SCROLL =================
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # ================= SCROLL FRAME =================
        self.scrollable_frame = tk.Frame(self.canvas)

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="n"
        )

        # auto resize canvas width
        def resize_canvas(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)

        self.canvas.bind("<Configure>", resize_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # ================= CENTER WRAPPER =================
        self.center = tk.Frame(self.scrollable_frame)
        self.center.pack(expand=True)

        # grid layout 2 columns
        self.center.grid_columnconfigure(0, weight=1)
        self.center.grid_columnconfigure(1, weight=1)

        # ================= CARDS =================

        # 🚗 VEHICLE CARD (LEFT)
        self.vehicle_card = tk.LabelFrame(
            self.center,
            text="🚗 Informations véhicule",
            padx=20,
            pady=15
        )
        self.vehicle_card.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        # 👤 OWNER CARD (RIGHT)
        self.owner_card = tk.LabelFrame(
            self.center,
            text="👤 Propriétaire",
            padx=20,
            pady=15
        )
        self.owner_card.grid(row=0, column=1, padx=20, pady=20, sticky="n")


        # Initialiser pour éviter les erreurs
        self.owner_map = {}
        self.owners = []


        # ================= BUILD FORMS =================
        self.build_vehicle_form()

        self.build_owner_section()

        # Charger les données
        self.load_owners()

        # ================= BUTTON =================
        tk.Button(
            self.center,
            text="💾 Enregistrer",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=25,
            command=self.save
        ).grid(row=1, column=0, columnspan=2, pady=25)

    # ================= VEHICLE FORM =================
    def build_vehicle_form(self):

        self.marque = self.entry(self.vehicle_card, "Marque", 0)
        self.modele = self.entry(self.vehicle_card, "Modèle", 1)
        self.puissance = self.entry(self.vehicle_card, "Puissance", 2)
        self.cylindre = self.entry(self.vehicle_card, "Cylindre", 3)

        tk.Label(self.vehicle_card, text="Type").grid(row=4, column=0, sticky="w", pady=5)
        self.type = ttk.Combobox(self.vehicle_card, values=["Moto", "Voiture"], width=28)
        self.type.grid(row=4, column=1)

        self.annee = self.entry(self.vehicle_card, "Année", 5)
        self.valeur = self.entry(self.vehicle_card, "Valeur", 6)

        tk.Label(self.vehicle_card, text="Usage").grid(row=7, column=0, sticky="w", pady=5)
        self.usage = ttk.Combobox(self.vehicle_card, values=["Personnel", "Transport"], width=28)
        self.usage.grid(row=7, column=1)

        tk.Label(self.vehicle_card, text="Places").grid(row=8, column=0, sticky="w", pady=5)
        self.places = ttk.Combobox(self.vehicle_card, values=[2, 5, 7, 9, 15, 22, 30], width=28)
        self.places.grid(row=8, column=1)

        self.immatriculation = self.entry(self.vehicle_card, "Immatriculation", 9)

    # ================= OWNER SECTION =================
    def build_owner_section(self):

        # existing owner
        self.owner_select_frame = tk.Frame(self.owner_card)
        self.owner_select_frame.grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(self.owner_select_frame, text="Propriétaire existant").grid(row=0, column=0, padx=10)

        self.owner_search = tk.StringVar()
        self.owner_combo = ttk.Combobox(
            self.owner_select_frame,
            textvariable=self.owner_search,
            width=30
        )
        self.owner_combo.grid(row=0, column=1, padx=10)

        self.owner_combo.bind("<KeyRelease>", self.filter_owners)

        # switch
        self.is_new_owner = tk.BooleanVar(value=False)

        tk.Checkbutton(
            self.owner_card,
            text="➕ Nouveau propriétaire",
            variable=self.is_new_owner,
            command=self.toggle_owner_mode
        ).grid(row=1, column=0, columnspan=2, pady=10)

        # new owner
        self.new_owner_frame = tk.Frame(self.owner_card)
        self.new_owner_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.build_owner_form()
        self.new_owner_frame.grid_remove()

    # ================= OWNER FORM =================
    def build_owner_form(self):

        self.nom = self.entry(self.new_owner_frame, "Nom", 0)
        self.prenom = self.entry(self.new_owner_frame, "Prénom", 1)
        tk.Label(self.new_owner_frame, text="Date permis").grid(row=2, column=0, sticky="w", pady=5)
        self.date_permis = DateEntry(
            self.new_owner_frame,
            width=27,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-mm-dd"
        )
        self.date_permis.grid(row=2, column=1, pady=5)

        tk.Label(self.new_owner_frame, text="Date naissance").grid(row=3, column=0, sticky="w", pady=5)
        self.date_naissance = DateEntry(
            self.new_owner_frame,
            width=27,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-mm-dd"
        )
        self.date_naissance.grid(row=3, column=1, pady=5)
        tk.Label(self.new_owner_frame, text="Aptitude").grid(row=4, column=0)
        self.aptitude = ttk.Combobox(self.new_owner_frame, values=["Réduite", "Normale"], width=28)
        self.aptitude.grid(row=4, column=1)

        self.adresse = self.entry(self.new_owner_frame, "Adresse", 5)
        
        tk.Label(self.new_owner_frame, text="Sexe").grid(row=6, column=0)

        self.sexe_map = {
            "Homme": 1,
            "Femme": 0
        }

        self.sexe = ttk.Combobox(
            self.new_owner_frame,
            values=list(self.sexe_map.keys()),
            width=28,
            state="readonly"
        )
        self.sexe.grid(row=6, column=1)

        # ✅ valeur par défaut = Homme (index 0)
        self.sexe.current(0)

    # ================= ENTRY =================
    def entry(self, frame, label, row):
        tk.Label(frame, text=label, width=18, anchor="w").grid(
            row=row, column=0, sticky="w", pady=5
        )
        e = tk.Entry(frame, width=30)
        e.grid(row=row, column=1, pady=5)
        return e

    # ================= TOGGLE =================
    def toggle_owner_mode(self):
        if self.is_new_owner.get():
            self.owner_select_frame.grid_remove()
            self.new_owner_frame.grid()
        else:
            self.new_owner_frame.grid_remove()
            self.owner_select_frame.grid()


    # ================= SAVE =================
    def save(self):
        data = {
            "marque": self.marque.get(),
            "modele": self.modele.get(),
            "puissance": self.puissance.get(),
            "cylindre": self.cylindre.get(),
            "type": self.type.get(),
            "nombre_place": self.places.get(),
            "usage": self.usage.get(),
            "valeur": self.valeur.get(),
            "immatriculation": self.immatriculation.get(),
            "annee": self.annee.get(),
        }

        if self.is_new_owner.get():

            owner = {
                "nom": self.nom.get(),
                "prenom": self.prenom.get(),
                "naissance": self.date_naissance.get(),
                "permis": self.date_permis.get(),
                "adresse": self.adresse.get(),
                "sexe": self.sexe_map.get(self.sexe.get()),
                "aptitude": self.aptitude.get()
            }
            data["proprietaire_id"] = ajouter_client(owner["nom"], owner["prenom"], owner["naissance"], owner["permis"], owner["adresse"], owner["sexe"], owner["aptitude"])
            
            proprio = get_owner(data["proprietaire_id"])
            profil = self.calcul_profil(proprio)

            labelProfils = ["Prudent", "Normal", "Risqué"]

            textProf = labelProfils[profil]

            insert_profil(data["proprietaire_id"], datetime.now(), textProf, "RNA")

        else:
            selected_name = self.owner_combo.get()
            owner_id = self.owner_map.get(selected_name)

            if not owner_id:
                messagebox.showerror("Erreur", "Propriétaire invalide")
                return

            data["proprietaire_id"] = owner_id

        v_id = ajouter_vehicule_db(data["proprietaire_id"], data["marque"], data["modele"], data["puissance"], data["cylindre"], data["type"], data["nombre_place"], data["usage"], data["valeur"], data["immatriculation"], data["annee"])
        
        if self.refresh_callback:
            self.refresh_callback()
        
        messagebox.showinfo("Succès", "Véhicule ajouté avec succès")    
        
        vehicle = get_vehicle(v_id)
        
        saisons = get_all_seasons()
        
        for saison in saisons:
            niveau_risk = self.calcul_risque(vehicle, saison)
            
            labelNiveaux = ["Faible", "Moyen", "Élevé"]

            textNiv = labelNiveaux[niveau_risk]

            insert_risk(vehicle.id, saison.id, textNiv, "RNA", datetime.now(), "Calcul saisonnier")
        
        niveaux = get_niveau_risque(vehicle.id)

        for niveau in niveaux:
            frais = self.calcul_frais(niveau, 0)
            frais = round(frais, 2) * 1000
            insert_frais(frais, niveau.id)

    # ================= LOAD OWNERS =================
    def load_owners(self):
   
        self.owners = charger_clients()
        print("Liste des propriétaires :", self.owners)
        self.owner_map = {f"{o[1]} {o[2]}": o[0] for o in self.owners}
        self.owner_combo["values"] = list(self.owner_map.keys())

    # ================= FILTER OWNERS =================
    def filter_owners(self, event):
        typed = self.owner_search.get().lower()
        self.owner_combo["values"] = [
            name for name in self.owner_map.keys()
            if typed in name.lower()
        ]

    # ================= IA =================

    
    def calcul_profil(self,owner):
        age = 2026 - int(owner.date_naissance.year)
        permis = 2026 - int(owner.date_permis.year)
        sexe = int(owner.sexe)
        aptitude = 1 if owner.aptitude_conduite == "Normale" else 0

        x = [
            sexe,
            age / 100,
            permis / 50,
            aptitude
        ]

        res = profil_model.predict(x)
        return res


    def calcul_risque(self,vehicule,saison):
        saison_type = 1 if saison.type == "Sec" else 0
        saison_periode = 0 if saison.periode == "Calme" else 1 if saison.periode == "Fête" else 2
        v_type = 1 if vehicule.type == "Voiture" else 0
        profilProprio = 0 if vehicule.proprietaire.profils[0].profil == "Prudent" else 1 if vehicule.proprietaire.profils[0].profil == "Normal" else 2
        
        x = [
            profilProprio / 2,
            saison.mois / 12,
            float(vehicule.puissance or 0) / 400,
            1 - ((int(vehicule.annee or 2000) - 1800) / (2026 - 1800)),
            v_type,
            saison_type,
            saison_periode / 2,
            0
        ]

        res = risque_model.predict(x)
        return res
       
    def calcul_frais(self, niveau, tarif):
        niv_risk = 0 if niveau.niveau_risk == "Faible" else 1 if niveau.niveau_risk == "Moyen" else 2
        risque = niv_risk / 2
        typev = 1 if niveau.vehicule.type == "Voiture" else 0
        places = float(niveau.vehicule.nombre_place or 0) / 30
        usage = 1 if niveau.vehicule.usage == "Transport" else 0
        tarif = tarif
        valeur = float(niveau.vehicule.valeur or 0)
        if typev == 0:
            valeur /= 50000000
        else:
            valeur /= 100000000

        x = [risque, typev, places, usage, tarif, valeur]

        res = frais_model.predict(x)

        return res
