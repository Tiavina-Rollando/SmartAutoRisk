import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from controllers.vehicule_controller import *
from services.recuperation import get_vehicle


# =====================================================
# CARD REUTILISABLE RESPONSIVE
# =====================================================
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


# =====================================================
# DETAIL VEHICULE VIEW
# =====================================================
class DetailVehiculeView:

    def __init__(self, root, vehicule_id, immatriculation):

        self.root = root
        self.immatriculation = immatriculation

        self.data = self.charger_detail(vehicule_id)

        root.title(f"SmartAutoRisk - {immatriculation}")
        root.state("zoomed")
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
        ).pack(side="right", padx=20, pady=5)

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
        # self.create_profil_card()
        self.create_risque_card()

        self.create_proprietaire_card()
        self.create_vehicule_card()
        # self.create_accident_card()

    # =====================================================
    # DATA
    # =====================================================
    def charger_detail(self, vehicule_id):
        vehicule = get_vehicle(vehicule_id)

        profil_obj = next(iter(vehicule.proprietaire.profils), None)

        return {
            "marque": vehicule.marque,
            "modele": vehicule.modele,
            "cylindre": vehicule.cylindre*1000,
            "puissance": vehicule.puissance,
            "type": vehicule.type,
            "nombre_place": vehicule.nombre_place,
            "usage": vehicule.usage,
            "valeur": vehicule.valeur,
            "immatriculation": vehicule.immatriculation,

            "profil_p": profil_obj.profil if profil_obj else "N/A",

            "nom_p": vehicule.proprietaire.nom,
            "prenom_p": vehicule.proprietaire.prenom,
            "date_permis_p": vehicule.proprietaire.date_permis.strftime("%d/%m/%Y")
                if vehicule.proprietaire.date_permis else "",
            "adresse_p": vehicule.proprietaire.adresse,
            "date_naissance_p": vehicule.proprietaire.date_naissance.strftime("%d/%m/%Y")
                if vehicule.proprietaire.date_naissance else "",
            "aptitude_conduite_p": vehicule.proprietaire.aptitude_conduite,

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

    # =====================================================
    # UTILS
    # =====================================================
    def int_to_mois(self, m):
        return ["Jan","Fev","Mar","Avr","Mai","Juin","Juil","Aout","Sep","Oct","Nov","Dec"][m-1] if m else ""

    # =====================================================
    # ASSURANCE
    # =====================================================
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

    # =====================================================
    # PROFIL
    # =====================================================
    def create_profil_card(self):

        frame, content = create_card(self.middle, "Profil")
        frame.pack(fill="both", expand=True, pady=10)

        profil = self.data["profil_p"]

        colors = {"Prudent":"#3498db","Normal":"#f1c40f","Risqué":"#e74c3c"}

        canvas = tk.Canvas(content, bg="white", height=200)
        canvas.pack(fill="both", expand=True)

        canvas.create_oval(50, 30, 150, 130, fill=colors.get(profil, "#95a5a6"))
        canvas.create_text(100, 80, text=profil, fill="white")

    # =====================================================
    # RISQUE RESPONSIVE
    # =====================================================
    def create_risque_card(self):

        frame, content = create_card(self.middle, "Risque")
        frame.pack(fill="both", expand=True, pady=10)

        risques = self.data.get("risques", [])

        mois = [self.int_to_mois(r["mois"]) for r in risques]
        scores = [r["niveau"] for r in risques]

        fig = Figure()
        ax = fig.add_subplot(111)

        ax.bar(mois, scores)
        # ✅ Y classification 
        ax.set_yticks([1, 2, 3]) 
        ax.set_yticklabels(["Faible", "Moyen", "Élevé"], fontweight="bold")

        canvas = FigureCanvasTkAgg(fig, master=content)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # =====================================================
    # TABLES
    # =====================================================
    def create_proprietaire_card(self):

        frame, content = create_card(self.right, "Propriétaire")
        frame.pack(fill="both", expand=True, pady=10)

        # ================= HEADER BADGE =================
        header = tk.Frame(content, bg="white")
        header.pack(fill="x", pady=(5, 10))

        profil = self.data["profil_p"]

        colors = {
            "Prudent": "#3498db",
            "Normal": "#f1c40f",
            "Risqué": "#e74c3c"
        }

        badge_color = colors.get(profil, "#95a5a6")

        badge = tk.Label(
            header,
            text=profil,
            bg=badge_color,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=4
        )
        badge.pack(side="right")

        # ================= INFOS =================
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

            tk.Label(
                container,
                text=label + " :",
                font=("Segoe UI", 10, "bold"),
                bg="white",
                width=15,
                anchor="w"
            ).grid(row=i, column=0, sticky="w", pady=3)

            tk.Label(
                container,
                text=value,
                font=("Segoe UI", 10),
                bg="white",
                anchor="w"
            ).grid(row=i, column=1, sticky="w", pady=3)


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

            tk.Label(
                container,
                text=label + " :",
                font=("Segoe UI", 10, "bold"),
                bg="white",
                width=15,
                anchor="w"
            ).grid(row=i, column=0, sticky="w", pady=2)

            tk.Label(
                container,
                text=value,
                font=("Segoe UI", 10),
                bg="white",
                anchor="w"
            ).grid(row=i, column=1, sticky="w", pady=2)

    def create_accident_card(self):

        frame, content = create_card(self.right, "Historique Accidents")
        frame.pack(fill="both", expand=True, pady=10)

        headers = ["Date", "Lieu", "Gravité", "Type", "Dégât", "Rôle"]

        accidents = charger_accidents_vehicule(self.immatriculation)

        table = tk.Frame(content, bg="white")
        table.pack(fill="both", expand=True)

        for i, h in enumerate(headers):
            tk.Label(table, text=h, font=("Segoe UI", 9, "bold"), bg="white").grid(row=0, column=i, padx=5)

        for r, a in enumerate(accidents):
            values = [
                a["date"].strftime("%d/%m/%Y") if a["date"] else "",
                a["lieu"],
                a["gravite"],
                a["type"],
                a["degat"],
                a["role"]
            ]

            for c, v in enumerate(values):
                tk.Label(table, text=v, bg="white").grid(row=r+1, column=c, padx=5)