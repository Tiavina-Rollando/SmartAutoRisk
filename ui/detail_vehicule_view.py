import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from database.models import vehicule
from controllers.vehicule_controller import *
from services.recuperation import get_vehicle
from ui.factures_view import FacturesView
from ui.contrat_view import ContratView

# ================= PALETTE DE COULEURS & DESIGN SYSTEM =================
COLOR_BG = "#F8FAFC"          # Fond principal (Slate 50)
COLOR_CARD_BG = "#FFFFFF"     # Fond des cartes
COLOR_BORDER = "#CBD5E1"      # Bordures et séparateurs (Slate 300)
COLOR_TEXT_PRIMARY = "#0F172A"# Texte principal (Slate 900)
COLOR_TEXT_SECONDARY = "#475569" # Texte secondaire (Slate 600)
COLOR_PRIMARY = "#2563EB"     # Bleu principal (Blue 600)
COLOR_PRIMARY_HOVER = "#1D4ED8" # Bleu survol (Blue 700)
COLOR_SUCCESS = "#10B981"     # Vert contrat (Emerald 500)
COLOR_SUCCESS_HOVER = "#059669" # Vert survol (Emerald 600)
COLOR_DANGER = "#EF4444"      # Rouge factures (Red 500)
COLOR_DANGER_HOVER = "#DC2626"  # Rouge survol (Red 600)

FONT_FAMILY = "Segoe UI"


def create_card(parent, title):
    frame = tk.Frame(parent, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)

    header_frame = tk.Frame(frame, bg=COLOR_CARD_BG)
    header_frame.pack(fill="x", padx=16, pady=(12, 4))

    header = tk.Label(
        header_frame,
        text=title,
        font=(FONT_FAMILY, 15, "bold"),
        fg=COLOR_TEXT_PRIMARY,
        bg=COLOR_CARD_BG,
        anchor="w"
    )
    header.pack(fill="x")

    separator = tk.Frame(frame, bg=COLOR_BORDER, height=1)
    separator.pack(fill="x", padx=16, pady=(4, 6))

    content = tk.Frame(frame, bg=COLOR_CARD_BG)
    content.pack(fill="both", expand=True, padx=16, pady=(0, 10))

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

        root.configure(bg=COLOR_BG)

        # ================= HEADER =================
        header = tk.Frame(root, bg=COLOR_BG)
        header.pack(fill="x", padx=20, pady=15)

        title_frame = tk.Frame(header, bg=COLOR_BG)
        title_frame.pack(side="left", fill="y")

        tk.Label(
            title_frame,
            text=f"Véhicule {immatriculation}",
            font=(FONT_FAMILY, 26, "bold"),
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_BG
        ).pack(anchor="w")

        tk.Label(
            title_frame,
            text="Vue détaillée des risques, tarifs et informations générales",
            font=(FONT_FAMILY, 13),
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_BG
        ).pack(anchor="w", pady=(2, 0))

        # Zone des boutons avec taille fixe uniformisée
        btn_container = tk.Frame(header, bg=COLOR_BG)
        btn_container.pack(side="right", anchor="center")

        btn_kwargs = {
            "font": (FONT_FAMILY, 11, "bold"),
            "fg": "white",
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2",
            "width": 18,
            "height": 2
        }

        # Ordre d'affichage : Contrats -> Factures -> Retour
        btn_contrat = tk.Button(
            btn_container,
            text="📄 Contrats",
            command=self.ouvrir_gestion_contrat,
            bg=COLOR_SUCCESS,
            activebackground=COLOR_SUCCESS_HOVER,
            activeforeground="white",
            **btn_kwargs
        )
        btn_contrat.pack(side="left", padx=6)

        btn_factures = tk.Button(
            btn_container,
            text="💳 Factures",
            command=self.ouvrir_factures,
            bg=COLOR_DANGER,
            activebackground=COLOR_DANGER_HOVER,
            activeforeground="white",
            **btn_kwargs
        )
        btn_factures.pack(side="left", padx=6)

        btn_retour = tk.Button(
            btn_container,
            text="← Retour",
            command=root.destroy,
            bg=COLOR_PRIMARY,
            activebackground=COLOR_PRIMARY_HOVER,
            activeforeground="white",
            **btn_kwargs
        )
        btn_retour.pack(side="left", padx=(6, 0))

        # ================= BODY GRID =================
        body = tk.Frame(root, bg=COLOR_BG)
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_columnconfigure(2, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self.left = tk.Frame(body, bg=COLOR_BG)
        self.middle = tk.Frame(body, bg=COLOR_BG)
        self.right = tk.Frame(body, bg=COLOR_BG)

        self.left.grid(row=0, column=0, sticky="nsew", padx=8, pady=5)
        self.middle.grid(row=0, column=1, sticky="nsew", padx=8, pady=5)
        self.right.grid(row=0, column=2, sticky="nsew", padx=8, pady=5)

        # ================= CARDS =================
        self.create_assurance_card()
        self.create_risque_card()
        self.create_accident_card()
        self.create_proprietaire_card()
        self.create_vehicule_card()

    def ouvrir_factures(self):
        if self.vehicule_id:
            FacturesView(self.root, vehicule_id=self.vehicule_id)
        else:
            messagebox.showwarning(
                "Information",
                "Impossible d'ouvrir les factures : identifiant du véhicule introuvable.",
                parent=self.root
            )

    def ouvrir_gestion_contrat(self):
        mois_actuel = datetime.now().month

        risques = self.data.get("risques", [])
        niveau_risk_mois = 1

        for r in risques:
            if r.get("mois") == mois_actuel:
                niveau_risk_mois = r.get("niveau", 1)
                break

        valeur = float(self.data.get("valeur", 20000000))
        puissance = float(self.data.get("puissance", 5))

        base_tarif = (valeur * 0.015) + (puissance * 2000)
        montant_calcule = base_tarif * (1 + (niveau_risk_mois * 0.1))

        self.data['montant_graphe'] = int(montant_calcule)
        ContratView(self.root, vehicule_id=self.vehicule_id, data_vehicule=self.data)

    def charger_detail(self, vehicule_id):
        vehicule = get_vehicle(vehicule_id)
        if not vehicule:
            return {}

        proprietaire = getattr(vehicule, "proprietaire", None)
        contrats = getattr(vehicule, "contrats", [])
        risques_list = getattr(vehicule, "risques", []) or []

        profils = getattr(proprietaire, "profils", []) if proprietaire else []
        profil_obj = profils[0] if profils else None
        contrat_obj = contrats[0] if contrats else None

        frais_list = []
        for r in risques_list:
            for f in (getattr(r, "frais", []) or []):
                hist_risk = getattr(f, "historique_risk", None)
                saison = getattr(hist_risk, "saison", None) if hist_risk else None
                frais_list.append({
                    "montant": getattr(f, "frais", 0),
                    "mois": getattr(saison, "mois", 0) if saison else 0
                })

        return {
            "contrat_id": getattr(contrat_obj, "id", None),
            "marque": getattr(vehicule, "marque", ""),
            "modele": getattr(vehicule, "modele", ""),
            "cylindre": (vehicule.cylindre * 1000) if getattr(vehicule, "cylindre", None) else 0,
            "puissance": getattr(vehicule, "puissance", 0),
            "type": getattr(vehicule, "type", ""),
            "nombre_place": getattr(vehicule, "nombre_place", 0),
            "usage": getattr(vehicule, "usage", ""),
            "valeur": getattr(vehicule, "valeur", 0),
            "immatriculation": getattr(vehicule, "immatriculation", ""),

            "profil_p": getattr(profil_obj, "profil", "N/A") if profil_obj else "N/A",
            "nom_p": getattr(proprietaire, "nom", "N/A") if proprietaire else "N/A",
            "prenom_p": getattr(proprietaire, "prenom", "") if proprietaire else "",
            "date_permis_p": proprietaire.date_permis.strftime("%d/%m/%Y")
                if proprietaire and getattr(proprietaire, "date_permis", None) else "",
            "adresse_p": getattr(proprietaire, "adresse", "") if proprietaire else "",
            "date_naissance_p": proprietaire.date_naissance.strftime("%d/%m/%Y")
                if proprietaire and getattr(proprietaire, "date_naissance", None) else "",
            "aptitude_conduite_p": getattr(proprietaire, "aptitude_conduite", "") if proprietaire else "",

            "risques": [
                {
                    "mois": r.saison.mois if getattr(r, "saison", None) else 0,
                    "niveau": 1 if r.niveau_risk == "Faible" else 2 if r.niveau_risk == "Moyen" else 3,
                }
                for r in risques_list
            ],
            "frais": frais_list
        }

    def int_to_mois(self, m):
        return ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin", "Juil", "Aout", "Sep", "Oct", "Nov", "Dec"][m - 1] if 1 <= m <= 12 else ""

    def create_assurance_card(self):
        frame, content = create_card(self.left, "Prix Assurance")
        frame.pack(fill="both", expand=True, pady=8)

        frais = self.data.get("frais", [])
        if not frais:
            tk.Label(content, text="Aucune donnée d'assurance disponible", bg=COLOR_CARD_BG, fg=COLOR_TEXT_SECONDARY, font=(FONT_FAMILY, 11)).pack(pady=20)
            return

        mois = [self.int_to_mois(f["mois"]) for f in frais]
        prix = [f["montant"] for f in frais]

        fig = Figure(figsize=(5, 3.2), dpi=100, facecolor=COLOR_CARD_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLOR_CARD_BG)

        ax.plot(mois, prix, marker="o", color=COLOR_PRIMARY, linewidth=2.5, markersize=7, markerfacecolor="white", markeredgewidth=2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COLOR_BORDER)
        ax.spines['bottom'].set_color(COLOR_BORDER)
        ax.tick_params(colors=COLOR_TEXT_SECONDARY, labelsize=11)
        ax.grid(axis='y', linestyle='--', alpha=0.5, color=COLOR_BORDER)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=content)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_risque_card(self):
        frame, content = create_card(self.middle, "Risque")
        frame.pack(fill="both", expand=True, pady=8)

        risques = self.data.get("risques", [])
        if not risques:
            tk.Label(content, text="Aucune donnée de risque disponible", bg=COLOR_CARD_BG, fg=COLOR_TEXT_SECONDARY, font=(FONT_FAMILY, 11)).pack(pady=20)
            return

        mois = [self.int_to_mois(r["mois"]) for r in risques]
        scores = [r["niveau"] for r in risques]

        fig = Figure(figsize=(5, 3.2), dpi=100, facecolor=COLOR_CARD_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLOR_CARD_BG)

        bars = ax.bar(mois, scores, color="#3B82F6", width=0.55, edgecolor="none")
        colors_map = {1: "#10B981", 2: "#F59E0B", 3: "#EF4444"}
        for bar, score in zip(bars, scores):
            bar.set_color(colors_map.get(score, "#3B82F6"))

        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(["Faible", "Moyen", "Élevé"], fontweight="bold", color=COLOR_TEXT_SECONDARY, fontsize=11)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COLOR_BORDER)
        ax.spines['bottom'].set_color(COLOR_BORDER)
        ax.tick_params(colors=COLOR_TEXT_SECONDARY, labelsize=11)
        ax.grid(axis='y', linestyle='--', alpha=0.5, color=COLOR_BORDER)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=content)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_proprietaire_card(self):
        frame, content = create_card(self.right, "Propriétaire")
        frame.pack(fill="x", pady=(8, 5))

        header = tk.Frame(content, bg=COLOR_CARD_BG)
        header.pack(fill="x", pady=(5, 10))

        profil = self.data.get("profil_p", "N/A")

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
            font=(FONT_FAMILY, 11, "bold"),
            padx=12,
            pady=4
        )
        badge.pack(side="right")

        infos = [
            ("Nom", self.data.get("nom_p", "-")),
            ("Prénom", self.data.get("prenom_p", "-")),
            ("Permis", self.data.get("date_permis_p", "-")),
            ("Adresse", self.data.get("adresse_p", "-")),
            ("Naissance", self.data.get("date_naissance_p", "-")),
            ("Aptitude", self.data.get("aptitude_conduite_p", "-"))
        ]

        container = tk.Frame(content, bg=COLOR_CARD_BG)
        container.pack(fill="x", padx=10, pady=5)
        container.grid_columnconfigure(1, weight=1)

        for i, (label, value) in enumerate(infos):
            tk.Label(
                container,
                text=label + " :",
                font=(FONT_FAMILY, 11, "bold"),
                fg=COLOR_TEXT_SECONDARY,
                bg=COLOR_CARD_BG,
                width=15,
                anchor="w"
            ).grid(row=i, column=0, sticky="w", pady=4)

            tk.Label(
                container,
                text=value if value else "-",
                font=(FONT_FAMILY, 11),
                fg=COLOR_TEXT_PRIMARY,
                bg=COLOR_CARD_BG,
                anchor="w"
            ).grid(row=i, column=1, sticky="w", pady=4)

    def create_vehicule_card(self):
        frame, content = create_card(self.right, "Véhicule")
        frame.pack(fill="x", pady=(5, 8))

        infos = [
            ("Marque", self.data.get("marque", "-")),
            ("Modèle", self.data.get("modele", "-")),
            ("Cylindre", str(self.data.get("cylindre", 0)) + " cc"),
            ("Puissance", str(self.data.get("puissance", 0)) + " ch"),
            ("Type", self.data.get("type", "-")),
            ("Places", str(self.data.get("nombre_place", 0))),
            ("Usage", self.data.get("usage", "-")),
            ("Valeur", str(self.data.get("valeur", 0)) + " MGA"),
            ("Immatriculation", self.data.get("immatriculation", "-"))
        ]

        container = tk.Frame(content, bg=COLOR_CARD_BG)
        container.pack(fill="x", padx=10, pady=5)
        container.grid_columnconfigure(1, weight=1)

        for i, (label, value) in enumerate(infos):
            tk.Label(
                container,
                text=label + " :",
                font=(FONT_FAMILY, 11, "bold"),
                fg=COLOR_TEXT_SECONDARY,
                bg=COLOR_CARD_BG,
                width=15,
                anchor="w"
            ).grid(row=i, column=0, sticky="w", pady=3)

            tk.Label(
                container,
                text=value if value else "-",
                font=(FONT_FAMILY, 11),
                fg=COLOR_TEXT_PRIMARY,
                bg=COLOR_CARD_BG,
                anchor="w"
            ).grid(row=i, column=1, sticky="w", pady=3)

    def create_accident_card(self):
        frame, content = create_card(self.middle, "Historique Accidents")
        frame.pack(fill="both", expand=True, pady=8)

        headers = ["Date", "Lieu", "Gravité", "Type", "Dégât", "Rôle"]
        accidents = charger_accidents_vehicule(self.immatriculation) if "charger_accidents_vehicule" in globals() else []

        if not accidents:
            tk.Label(content, text="Aucun accident enregistré", bg=COLOR_CARD_BG, fg=COLOR_TEXT_SECONDARY, font=(FONT_FAMILY, 11)).pack(pady=15)
            return

        table = tk.Frame(content, bg=COLOR_CARD_BG)
        table.pack(fill="both", expand=True)

        for i, h in enumerate(headers):
            tk.Label(table, text=h, font=(FONT_FAMILY, 10, "bold"), fg=COLOR_TEXT_SECONDARY, bg=COLOR_CARD_BG).grid(row=0, column=i, padx=4, pady=2, sticky="w")

        for r, a in enumerate(accidents):
            values = [
                a["date"].strftime("%d/%m/%Y") if a.get("date") else "",
                a.get("lieu", ""),
                a.get("gravite", ""),
                a.get("type", ""),
                a.get("degat", ""),
                a.get("role", "")
            ]

            for c, v in enumerate(values):
                tk.Label(table, text=v, font=(FONT_FAMILY, 10), fg=COLOR_TEXT_PRIMARY, bg=COLOR_CARD_BG).grid(row=r + 1, column=c, padx=4, pady=2, sticky="w")