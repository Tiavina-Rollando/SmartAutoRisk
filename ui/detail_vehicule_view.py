import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from controllers.vehicule_controller import *
from services.recuperation import get_vehicle


# =====================================================
# CARD MODERNE REUTILISABLE
# =====================================================
def create_card(parent, title, height=130):

    card = tk.Frame(parent, bg="#ffffff", height=height, width=600)
    card.pack(fill="x", pady=10, padx=10)
    card.pack_propagate(False)

    tk.Label(
        card,
        text=title,
        font=("Segoe UI", 13, "bold"),
        fg="#2e6de6",
        bg="#ffffff"
    ).pack(anchor="center", pady=5)

    content = tk.Frame(card, bg="#ffffff")
    content.pack(expand=True)

    return content


# =====================================================
# CLASSE DETAIL VEHICULE
# =====================================================
class DetailVehiculeView:

    def __init__(self, root, vehicule_id, immatriculation):

        self.root = root
        self.immatriculation = immatriculation
        diag = self.charger_detail(vehicule_id)
        self.data = charger_detail_vehicule(vehicule_id)

        root.title(f"SmartAutoRisk - Véhicule {immatriculation}")
        root.state("zoomed")
        root.configure(bg="#f2f4f8")

        # =============================
        # TITRE
        # =============================
        tk.Label(
            root,
            text=f"Détails véhicule : {immatriculation}",
            font=("Arial", 24, "bold"),
            bg="#f2f4f8"
        ).pack(pady=25)

        # =============================
        # HEADER
        # =============================
        header = tk.Frame(root, bg="#f2f4f8")
        header.pack(fill="x")

        tk.Button(header,
                  text="Retour",
                  bg="#2e6de6",
                  fg="white",
                  font=("Segoe UI", 11, "bold"),
                  relief="flat",
                  command=root.destroy).pack(side="right", padx=20)

        # =====================================================
        # BODY DASHBOARD
        # =====================================================
        body = tk.Frame(root, bg="#f2f4f8")
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg="#f2f4f8", width=550)
        left.pack(side="left", fill="y", padx=20)

        middle = tk.Frame(body, bg="#f2f4f8", width=350)
        middle.pack(side="left", fill="y")

        right = tk.Frame(body, bg="#f2f4f8", width=650)
        right.pack(side="left", fill="y", padx=40)

        # =============================
        # GRAPHIQUES
        # =============================
        self.create_assurance_card(left,diag)
        self.create_profil_card(middle,diag)
        self.create_risque_card(middle,diag)

        # =============================
        # TABLES
        # =============================
        self.create_proprietaire_card(right)
        self.create_vehicule_card(right)
        self.create_accident_card(right)


    def charger_detail(self, vehicule_id):
        vehicule = get_vehicle(vehicule_id)

        profil_obj = next(iter(vehicule.proprietaire.profils), None)

        data = {
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
                    "saison": r.saison.type if r.saison else "",
                    "mois": r.saison.mois if r.saison else 0,
                    "niveau": 1 if r.niveau_risk is "Faible" else 2 if r.niveau_risk is "Moyen" else 3,
                    "date": r.date_evaluation.strftime("%d/%m/%Y") if r.date_evaluation else "",
                    "source": r.source,
                    "commentaire": r.commentaire
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

        return data
    
    # =====================================================
    # GRAPH 1 — PRIX ASSURANCE
    # =====================================================
    def create_assurance_card(self, parent, data):

        card = tk.Frame(parent, bg="white")
        card.pack(fill="both", expand=True, pady=20)

        tk.Label(card,
                 text="Variation Prix Assurance",
                 font=("Segoe UI", 14, "bold"),
                 fg="#2e6de6",
                 bg="white").pack(pady=10)

        mois = ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin",
                "Juil", "Aout", "Sep", "Oct", "Nov", "Dec"]

        prices = data.get("frais", [])
        prix = [f["montant"] for f in prices] if prices else [0] * 12

        fig = Figure(figsize=(4.5, 4.5))
        ax = fig.add_subplot(111)

        ax.plot(mois, prix, marker="o")
        ax.set_title("Prix assurance par mois")
        ax.set_ylabel("Montant (Ar)")

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # =====================================================
    # GRAPH 2 — PROFIL IA
    # =====================================================
    def create_profil_card(self, parent, data):

        card = tk.Frame(parent, bg="white")
        card.pack(fill="both", pady=20)

        tk.Label(
            card,
            text="Profil Propriétaire",
            font=("Segoe UI", 13, "bold"),
            fg="#2e6de6",
            bg="white"
        ).pack(pady=8)

        # ================= PROFIL =================
        profil = data.get("profil_p", "N/A")

        colors = {
            "Prudent": "#3498db",   # bleu
            "Normal": "#f1c40f",    # jaune
            "Risqué": "#e74c3c"     # rouge
        }

        color = colors.get(profil, "#95a5a6")

        canvas = tk.Canvas(card, width=150, height=150, bg="white", highlightthickness=0)
        canvas.pack(pady=10)

        # cercle
        canvas.create_oval(20, 20, 130, 130, fill=color, outline="")

        # texte au centre
        canvas.create_text(
            75, 75,
            text=profil,
            fill="white",
            font=("Segoe UI", 11, "bold")
        )

    # =====================================================
    # GRAPH 3 — RISQUE RNA
    # =====================================================
    def create_risque_card(self, parent, data):

        card = tk.Frame(parent, bg="white")
        card.pack(fill="both", pady=20)

        tk.Label(card,
                 text="Niveau de Risque",
                 font=("Segoe UI", 13, "bold"),
                 fg="#2e6de6",
                 bg="white").pack(pady=8)

        annees = ["2019", "2020", "2021", "2022", "2023", "2024","2025","2026","2027","2028","2029","2030"]
        risques = data.get("risques", [])

        risque_score = [r["niveau"] for r in risques]

        if not risque_score:
            risque_score = [0] * 12

        fig = Figure(figsize=(4, 3))
        ax = fig.add_subplot(111)

        # ✅ BAR CHART
        ax.bar(annees, risque_score)

        # ✅ Y classification
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(["Faible", "Moyen", "Élevé"], fontsize=8)

        ax.set_xlabel("Année", fontsize=9)
        ax.set_title("Score de Risque", fontsize=10)

        ax.tick_params(axis='x', labelsize=8)

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # =====================================================
    # PROPRIETAIRE
    # =====================================================
    def create_proprietaire_card(self, parent):

        prop = create_card(parent, "Propriétaire")

        headers = ["Nom", "Prénom", "Permis", "Adresse",
                   "Naissance", "Aptitude"]

        values = [
            self.data["nom"],
            self.data["prenom"],
            self.data["date_permis"],
            self.data["adresse"],
            self.data["date_naissance"],
            self.data["aptitude_conduite"]
        ]

        for i, h in enumerate(headers):
            tk.Label(prop, text=h,
                     font=("Segoe UI", 9, "bold"),
                     bg="#ffffff").grid(row=0, column=i, padx=8)

        for i, v in enumerate(values):
            tk.Label(prop, text=v,
                     bg="#ffffff").grid(row=1, column=i, padx=8)

    # =====================================================
    # VEHICULE
    # =====================================================
    def create_vehicule_card(self, parent):

        veh = create_card(parent, "Véhicule")

        headers = ["Puissance", "Type", "Places",
                   "Usage", "Valeur", "Immatriculation"]

        values = [
            self.data["puissance"],
            self.data["type"],
            self.data["nombre_place"],
            self.data["usage"],
            self.data["valeur"],
            self.data["immatriculation"]
        ]

        for i, h in enumerate(headers):
            tk.Label(veh, text=h,
                     font=("Segoe UI", 9, "bold"),
                     bg="#ffffff").grid(row=0, column=i, padx=8)

        for i, v in enumerate(values):
            tk.Label(veh, text=v,
                     bg="#ffffff").grid(row=1, column=i, padx=8)

    # =====================================================
    # ACCIDENTS SQL
    # =====================================================
    def create_accident_card(self, parent):

        acc = create_card(parent, "Historique Accidents", height=170)

        headers = ["Date", "Lieu", "Gravité",
                   "Type", "Dégât", "Rôle"]

        accidents = charger_accidents_vehicule(self.immatriculation)

        for i, h in enumerate(headers):
            tk.Label(acc,
                     text=h,
                     font=("Segoe UI", 9, "bold"),
                     bg="#ffffff").grid(row=0, column=i, padx=8)

        for r, accident in enumerate(accidents):

            values = [
                accident["date"].strftime("%d/%m/%Y") if accident["date"] else "",
                accident["lieu"],
                accident["gravite"].capitalize(),
                accident["type"].capitalize(),
                accident["degat"].capitalize(),
                accident["role"].capitalize()
            ]

            for c, val in enumerate(values):
                tk.Label(acc,
                         text=val,
                         bg="#ffffff").grid(row=r+1, column=c, padx=8)