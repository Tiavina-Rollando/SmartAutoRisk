import tkinter as tk
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from controllers.vehicule_controller import *
from services.recuperation import get_vehicle
from ui.contrat_view import ContratView  # Import de la vue contrat


def create_card(parent, title):
    frame = tk.Frame(parent, bg="white", bd=1, relief="solid")

    header = tk.Label(
        frame,
        text=title,
        font=("Segoe UI", 12, "bold"),
        fg="#2e6de6",
        bg="white"
    )
    header.pack(fill="x", pady=(5, 2))

    content = tk.Frame(frame, bg="white")
    content.pack(fill="both", expand=True, padx=5, pady=5)

    return frame, content


class DetailVehiculeView:

    def __init__(self, root, vehicule_id, immatriculation):

        self.root = root
        self.vehicule_id = vehicule_id
        self.immatriculation = immatriculation

        self.data = self.charger_detail(vehicule_id)

        root.title(f"SmartAutoRisk - {immatriculation}")
        try:
            root.state("zoomed")
        except tk.TclError:
            root.attributes("-zoomed", True)

        root.configure(bg="#f2f4f8")

        # ================= HEADER =================
        header = tk.Frame(root, bg="#f2f4f8")
        header.pack(fill="x")

        tk.Label(
            header,
            text=f"Véhicule {immatriculation}",
            font=("Arial", 20, "bold"),
            bg="#f2f4f8"
        ).pack(side="left", padx=20, pady=10)

        # Bouton Retour
        tk.Button(
            header,
            text="← Retour",
            command=root.destroy,
            bg="#2e6de6",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=6,
            relief="flat",
            cursor="hand2",
            activebackground="#1f4fbf",
            activeforeground="white"
        ).pack(side="right", padx=(5, 20), pady=5)

        # 📄 NOUVEAU BOUTON CONTRAT
        tk.Button(
            header,
            text="📄 Contrats",
            command=self.ouvrir_gestion_contrat,
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=6,
            relief="flat",
            cursor="hand2",
            activebackground="#219150",
            activeforeground="white"
        ).pack(side="right", padx=5, pady=5)

        # ================= BODY GRID =================
        body = tk.Frame(root, bg="#f2f4f8")
        body.pack(fill="both", expand=True)

        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_columnconfigure(2, weight=1)

        body.grid_rowconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        # ================= COLUMNS =================
        self.left = tk.Frame(body, bg="#f2f4f8")
        self.middle = tk.Frame(body, bg="#f2f4f8")
        self.right = tk.Frame(body, bg="#f2f4f8")

        self.left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.middle.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        # ================= CARDS =================
        self.create_assurance_card()
        self.create_risque_card()

        self.create_proprietaire_card()
        self.create_vehicule_card()

    def ouvrir_gestion_contrat(self):
        # 1. Date et mois d'aujourd'hui
        mois_actuel = datetime.now().month

        # 2. Récupération du risque correspondant au mois actuel depuis self.data
        risques = self.data.get("risques", [])
        niveau_risk_mois = 1  # Valeur par défaut (Faible = 1, Moyen = 2, Élevé = 3)
        
        for r in risques:
            if r.get("mois") == mois_actuel:
                niveau_risk_mois = r.get("niveau", 1)
                break

        # 3. Calcul du montant selon la formule métier (identique à la génération du graphe)
        valeur = float(self.data.get("valeur", 20000000))
        puissance = float(self.data.get("puissance", 5))

        # Base tarifaire
        base_tarif = (valeur * 0.015) + (puissance * 2000)
        
        # Application de la majoration du risque de la saison courante
        montant_calcule = base_tarif * (1 + (niveau_risk_mois * 0.1))

        # 4. Envoi du montant calculé dans data
        self.data['montant_graphe'] = int(montant_calcule)

        # 5. Ouverture de la vue Contrat
        ContratView(self.root, vehicule_id=self.vehicule_id, data_vehicule=self.data)

    def charger_detail(self, vehicule_id):
        vehicule = get_vehicle(vehicule_id)

        profil_obj = next(iter(vehicule.proprietaire.profils), None) if vehicule.proprietaire else None

        return {
            "marque": vehicule.marque,
            "modele": vehicule.modele,
            "cylindre": vehicule.cylindre * 1000 if vehicule.cylindre else 0,
            "puissance": vehicule.puissance,
            "type": vehicule.type,
            "nombre_place": vehicule.nombre_place,
            "usage": vehicule.usage,
            "valeur": vehicule.valeur,
            "immatriculation": vehicule.immatriculation,

            "profil_p": profil_obj.profil if profil_obj else "N/A",

            "nom_p": vehicule.proprietaire.nom if vehicule.proprietaire else "N/A",
            "prenom_p": vehicule.proprietaire.prenom if vehicule.proprietaire else "",
            "date_permis_p": vehicule.proprietaire.date_permis.strftime("%d/%m/%Y")
                if vehicule.proprietaire and vehicule.proprietaire.date_permis else "",
            "adresse_p": vehicule.proprietaire.adresse if vehicule.proprietaire else "",
            "date_naissance_p": vehicule.proprietaire.date_naissance.strftime("%d/%m/%Y")
                if vehicule.proprietaire and vehicule.proprietaire.date_naissance else "",
            "aptitude_conduite_p": vehicule.proprietaire.aptitude_conduite if vehicule.proprietaire else "",

            "risques": [
                {
                    "mois": r.saison.mois if r.saison else 0,
                    "niveau": 1 if r.niveau_risk == "Faible" else 2 if r.niveau_risk == "Moyen" else 3,
                }
                for r in (vehicule.risques or [])
            ],

            "frais": [
                {
                    "montant": f.frais,
                    "mois": f.historique_risk.saison.mois
                        if f.historique_risk and f.historique_risk.saison else 0,
                }
                for r in (vehicule.risques or [])
                for f in (r.frais or [])
            ]
        }

    def int_to_mois(self, m):
        return ["Jan","Fev","Mar","Avr","Mai","Juin","Juil","Aout","Sep","Oct","Nov","Dec"][m-1] if m else ""

    def create_assurance_card(self):
        frame, content = create_card(self.left, "Prix Assurance")
        frame.pack(fill="both", expand=True, pady=10)

        frais = self.data.get("frais", [])
        mois = [self.int_to_mois(f["mois"]) for f in frais]
        prix = [f["montant"] for f in frais]

        fig = Figure()
        ax = fig.add_subplot(111)
        ax.plot(mois, prix, marker="o")

        canvas = FigureCanvasTkAgg(fig, master=content)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_risque_card(self):
        frame, content = create_card(self.middle, "Risque")
        frame.pack(fill="both", expand=True, pady=10)

        risques = self.data.get("risques", [])
        mois = [self.int_to_mois(r["mois"]) for r in risques]
        scores = [r["niveau"] for r in risques]

        fig = Figure()
        ax = fig.add_subplot(111)
        ax.bar(mois, scores)
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(["Faible", "Moyen", "Élevé"], fontweight="bold")

        canvas = FigureCanvasTkAgg(fig, master=content)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_proprietaire_card(self):
        frame, content = create_card(self.right, "Propriétaire")
        frame.pack(fill="both", expand=True, pady=10)

        header = tk.Frame(content, bg="white")
        header.pack(fill="x", pady=(5, 10))

        profil = self.data["profil_p"]
        colors = {"Prudent": "#3498db", "Normal": "#f1c40f", "Risqué": "#e74c3c"}

        badge = tk.Label(
            header,
            text=profil,
            bg=colors.get(profil, "#95a5a6"),
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=4
        )
        badge.pack(side="right")

        infos = [
            ("Nom", self.data["nom_p"]),
            ("Prénom", self.data["prenom_p"]),
            ("Permis", self.data["date_permis_p"]),
            ("Adresse", self.data["adresse_p"]),
            ("Naissance", self.data["date_naissance_p"]),
            ("Aptitude", self.data["aptitude_conduite_p"])
        ]

        container = tk.Frame(content, bg="white")
        container.pack(fill="both", expand=True, padx=10)

        for i, (label, value) in enumerate(infos):
            tk.Label(container, text=label + " :", font=("Segoe UI", 10, "bold"), bg="white", width=15, anchor="w").grid(row=i, column=0, sticky="w", pady=3)
            tk.Label(container, text=value, font=("Segoe UI", 10), bg="white", anchor="w").grid(row=i, column=1, sticky="w", pady=3)

    def create_vehicule_card(self):
        frame, content = create_card(self.right, "Véhicule")
        frame.pack(fill="both", expand=True, pady=10)

        infos = [
            ("Marque", self.data["marque"]),
            ("Modèle", self.data["modele"]),
            ("Cylindre", str(self.data["cylindre"]) + " cc"),
            ("Puissance", str(self.data["puissance"]) + " CV"),
            ("Type", self.data["type"]),
            ("Places", str(self.data["nombre_place"])),
            ("Usage", self.data["usage"]),
            ("Valeur", str(self.data["valeur"]) + " MGA"),
            ("Immatriculation", self.data["immatriculation"])
        ]

        container = tk.Frame(content, bg="white")
        container.pack(fill="both", expand=True, padx=10, pady=5)

        for i, (label, value) in enumerate(infos):
            tk.Label(container, text=label + " :", font=("Segoe UI", 10, "bold"), bg="white", width=15, anchor="w").grid(row=i, column=0, sticky="w", pady=2)
            tk.Label(container, text=value, font=("Segoe UI", 10), bg="white", anchor="w").grid(row=i, column=1, sticky="w", pady=2)