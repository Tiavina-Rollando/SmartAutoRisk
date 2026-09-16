import random
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from services.recuperation import get_all_owner
from ui.liste_contrat_view import ListeContratView


class Dashboard(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="#F1F5F9")
        self.pack(fill="both", expand=True)

        self._init_styles()
        self._build_header()
        self._build_content()
        self.refresh_all()

    def _init_styles(self):
        """Configuration du thème personnalisé ttk avec grandes polices pour projection."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Couleurs principales
        self.PRIMARY = "#1E293B"
        self.ACCENT = "#0284C7"
        self.SUCCESS = "#10B981"
        self.BG_MAIN = "#F1F5F9"
        self.CARD_BG = "#FFFFFF"

        # Cartes & Conteneurs
        self.style.configure(
            "Card.TFrame", background=self.CARD_BG, relief="flat"
        )

        # Labels - Tailles agrandies
        self.style.configure(
            "CardTitle.TLabel",
            font=("Segoe UI", 16, "bold"),
            foreground=self.PRIMARY,
            background=self.CARD_BG,
        )
        self.style.configure(
            "ResultValue.TLabel",
            font=("Segoe UI", 15, "bold"),
            foreground=self.ACCENT,
            background=self.CARD_BG,
        )

        # Treeview (Tableau) - Hauteur et textes agrandis
        self.style.configure(
            "Custom.Treeview",
            background=self.CARD_BG,
            foreground="#334155",
            fieldbackground=self.CARD_BG,
            rowheight=38,  # Plus haut pour accueillir du texte plus grand
            font=("Segoe UI", 12),
            borderwidth=0,
        )
        self.style.configure(
            "Custom.Treeview.Heading",
            background="#E2E8F0",
            foreground="#1E293B",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
        )
        self.style.map(
            "Custom.Treeview",
            background=[("selected", "#E0F2FE")],
            foreground=[("selected", "#0369A1")],
        )

    def _build_header(self):
        """En-tête principal."""
        header = tk.Frame(self, bg=self.PRIMARY, height=75)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Titre agrandi
        tk.Label(
            header,
            text="SMART AUTORISK",
            bg=self.PRIMARY,
            fg="#F8FAFC",
            font=("Segoe UI", 18, "bold"),
        ).pack(side="left", padx=25)

        tk.Label(
            header,
            text="|   Dashboard Overview",
            bg=self.PRIMARY,
            fg="#94A3B8",
            font=("Segoe UI", 13),
        ).pack(side="left")

        # Action Button avec texte plus grand
        btn_contrats = tk.Button(
            header,
            text="📁  Liste des Contrats",
            command=self.ouvrir_liste_contrats,
            bg=self.SUCCESS,
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            font=("Segoe UI", 12, "bold"),
            padx=18,
            pady=8,
            relief="flat",
            bd=0,
            cursor="hand2",
        )
        btn_contrats.pack(side="right", padx=25)

    def _build_content(self):
        """Structure principale du tableau de bord."""
        container = tk.Frame(self, bg=self.BG_MAIN)
        container.pack(fill="both", expand=True, padx=25, pady=25)

        # ----------------- SECTION TABLEAU (GAUCHE) -----------------
        card_table = ttk.Frame(container, style="Card.TFrame", padding=20)
        card_table.pack(side="left", fill="both", expand=True, padx=(0, 12))

        # En-tête Tableau
        header_table_frame = tk.Frame(card_table, bg=self.CARD_BG)
        header_table_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(
            header_table_frame,
            text="Propriétaires d'Automobiles",
            style="CardTitle.TLabel",
        ).pack(side="left")

        btn_refresh = tk.Button(
            header_table_frame,
            text="🔄 Actualiser",
            command=self.refresh_all,
            bg="#F1F5F9",
            fg=self.PRIMARY,
            activebackground="#E2E8F0",
            font=("Segoe UI", 11, "bold"),
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            relief="flat",
        )
        btn_refresh.pack(side="right")

        # Frame Tableau + Scrollbar
        tree_frame = tk.Frame(card_table, bg=self.CARD_BG)
        tree_frame.pack(fill="both", expand=True)

        columns = (
            "Nom",
            "Genre",
            "Véhicules",
            "Profil",
            "Fréquence",
            "Dernier Paiement",
            "Taux",
        )
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse",
        )

        # Colonnes & Alignement (largeurs adaptées au texte plus grand)
        widths = [160, 90, 90, 110, 100, 130, 80]
        for col, w in zip(columns, widths):
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, anchor="w", width=w)

        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ----------------- SECTION GRAPHIQUE (DROITE) -----------------
        card_chart = ttk.Frame(container, style="Card.TFrame", padding=20)
        card_chart.pack(
            side="right", fill="both", expand=False, padx=(12, 0)
        )
        card_chart.config(width=450)  # Un peu plus large pour la lisibilité

        ttk.Label(
            card_chart,
            text="Taux de Paiement Mensuel",
            style="CardTitle.TLabel",
        ).pack(anchor="w", pady=(0, 15))

        self.chart_frame = tk.Frame(card_chart, bg=self.CARD_BG)
        self.chart_frame.pack(fill="both", expand=True)

        # Grand texte récapitulatif pour la présentation
        self.result_label = ttk.Label(card_chart, style="ResultValue.TLabel")
        self.result_label.pack(pady=(15, 0))

    def ouvrir_liste_contrats(self):
        """Ouvre la vue de liste des contrats."""
        ListeContratView(self)

    def refresh_all(self):
        """Recharge l'ensemble des données."""
        self.load_proprietaires()
        self.load_chart()

    def get_proprio(self):
        """Structure les données propriétaires."""
        data = get_all_owner()
        return [
            {
                "nom": f"{o.nom or ''} {o.prenom or ''}".strip(),
                "genre": "Homme" if o.sexe == 1 else "Femme",
                "nb_vehicules": len(o.vehicules),
                "profil": o.profils[0].profil if o.profils else "Aucun",
                "frequence": random.choice(["Mensuel", "Annuel"]),
                "dernier_paiement": random.choice(
                    ["Janvier", "Février", "Mars", "Avril"]
                ),
                "taux": f"{random.randint(10, 100)}%",
            }
            for o in data
        ]

    def load_proprietaires(self):
        """Insère les données dans le Treeview."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in self.get_proprio():
            self.tree.insert(
                "",
                "end",
                values=(
                    p["nom"],
                    p["genre"],
                    p["nb_vehicules"],
                    p["profil"],
                    p["frequence"],
                    p["dernier_paiement"],
                    p["taux"],
                ),
            )

    def load_chart(self):
        """Rendu graphique moderne (Donut chart) adapté à un écran de présentation."""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Calculs de données
        total_members = random.randint(15, 50)
        montant_par_personne = random.randint(50000, 300000)
        total_attendu = total_members * montant_par_personne
        payeurs = random.randint(5, total_members)
        montant_paye = payeurs * montant_par_personne
        montant_restant = max(0, total_attendu - montant_paye)

        # Figure Matplotlib épurée
        fig, ax = plt.subplots(figsize=(4, 4), facecolor="#FFFFFF")
        colors = ["#0284C7", "#E2E8F0"]

        wedges, texts, autotexts = ax.pie(
            [montant_paye, montant_restant],
            labels=["Payé", "Reste"],
            autopct="%1.0f%%",
            startangle=90,
            colors=colors,
            pctdistance=0.72,
            wedgeprops=dict(width=0.38, edgecolor="white", linewidth=2),
        )

        # Polices agrandies pour la partie graphique
        for text in texts:
            text.set_color("#1E293B")
            text.set_fontsize(12)
            text.set_weight("bold")
        for autotext in autotexts:
            autotext.set_color("#FFFFFF")
            autotext.set_fontsize(12)
            autotext.set_weight("bold")

        ax.set_title(
            "Répartition Générale",
            fontsize=13,
            pad=15,
            color="#1E293B",
            weight="bold",
        )

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Label récapitulatif avec grande taille de police
        self.result_label.config(
            text=f"Total : {montant_paye:,} Ar / {total_attendu:,} Ar".replace(
                ",", " "
            )
        )