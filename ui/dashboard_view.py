import tkinter as tk
from tkinter import ttk
import random

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from services.recuperation import get_all_owner


class Dashboard(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        # ================= STYLE =================
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Card.TFrame", background="white")
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Result.TLabel", font=("Segoe UI", 14, "bold"), foreground="#2c3e50")
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))

        # ================= HEADER =================
        header = tk.Frame(self, bg="#2c3e50", height=60)
        header.pack(fill="x")

        tk.Label(
            header,
            text="SMART AUTORISK - DASHBOARD",
            bg="#2c3e50",
            fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=15)

        # ================= MAIN CONTAINER =================
        container = tk.Frame(self, bg="#ecf0f1")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # ================= CARD TABLE =================
        card_table = ttk.Frame(container, style="Card.TFrame", padding=15)
        card_table.pack(side="left", fill="both", expand=True, padx=10)

        ttk.Label(card_table, text="Liste des Propriétaires", style="Title.TLabel").pack(anchor="w", pady=10)

        columns = ("Nom", "Genre", "Nb Véhicules", "Profil", "Fréquence", "Dernier Paiement", "Taux annuel")

        self.tree = ttk.Treeview(card_table, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(card_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # ================= CARD CHART =================
        card_chart = ttk.Frame(container, style="Card.TFrame", padding=15)
        card_chart.pack(side="right", fill="both", expand=True, padx=10)

        ttk.Label(card_chart, text="Taux de Paiement Mensuel", style="Title.TLabel").pack(anchor="w", pady=10)

        self.chart_frame = tk.Frame(card_chart)
        self.chart_frame.pack(fill="both", expand=True)

        self.result_label = ttk.Label(card_chart, style="Result.TLabel")
        self.result_label.pack(pady=10)

        # ================= BUTTON =================
        ttk.Button(
            card_table,
            text="Actualiser",
            command=self.refresh_all,
            style="Accent.TButton"
        ).pack(anchor="e", pady=5)

        # ================= INIT LOAD =================
        self.refresh_all()

    # ================= REFRESH GLOBAL =================
    def refresh_all(self):
        self.load_proprietaires()
        self.load_chart()

    # ================= DATA PROPRIETAIRES =================
    def get_proprio(self):
        data = get_all_owner()

        return [{
            "nom": f"{o.nom or ''} {o.prenom or ''}".strip(),
            "genre": "Homme" if o.sexe == 1 else "Femme",
            "nb_vehicules": len(o.vehicules),
            "profil": o.profils[0].profil if o.profils else "Aucun",
            "frequence": random.choice(["Mensuel", "Annuel"]),
            "dernier_paiement": random.choice(["Janvier", "Février", "Mars", "Avril"]),
            "taux": f"{random.randint(10, 100)}%"
        } for o in data]

    # ================= TABLE =================
    def load_proprietaires(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in self.get_proprio():
            self.tree.insert("", "end", values=(
                p["nom"],
                p["genre"],
                p["nb_vehicules"],
                p["profil"],
                p["frequence"],
                p["dernier_paiement"],
                p["taux"]
            ))

    # ================= CHART =================
    def load_chart(self):
        # clear old chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # ===== fake data =====
        total_members = random.randint(10, 50)
        montant_par_personne = random.randint(50000, 300000)

        total_attendu = total_members * montant_par_personne

        payeurs = random.randint(0, total_members)
        montant_paye = payeurs * montant_par_personne
        montant_restant = total_attendu - montant_paye

        # ===== chart =====
        fig, ax = plt.subplots(figsize=(4, 4))

        ax.pie(
            [montant_paye, montant_restant],
            labels=["Payé", "Restant"],
            autopct="%1.1f%%"
        )

        ax.set_title("Répartition des Paiements")

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # ===== label =====
        self.result_label.config(
            text=f"{montant_paye} Ar payé / {total_attendu} Ar"
        )