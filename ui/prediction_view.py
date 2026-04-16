import tkinter as tk
from tkinter import ttk

from RNA_PROFIL.rna_profil import NeuralNetwork as ProfilNN
from RNA_RISK.rna_risk import NeuralNetwork as RiskNN
from RNA_RATE.rna_rate import NeuralNetwork as FeeNN


# ================= MODELS =================
profil_model = ProfilNN(4, 5, 3)
profil_model.load_model("models/profil_model.json")

risque_model = RiskNN(8, 10, 3)
risque_model.load_model("models/risk_model.json")

frais_model = FeeNN(6, 6)
frais_model.load_model("models/rate_model.json")


# ================= VIEW =================
class Prediction(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        # ================= STYLE =================
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TLabel", background="white")
        style.configure("TFrame", background="white")
        style.configure("Card.TFrame", background="white")
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Sub.TLabel", font=("Segoe UI", 11))
        style.configure("Result.TLabel", font=("Segoe UI", 14, "bold"), foreground="#1f3a93")
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))

        # ================= BACKGROUND =================
        self.configure(bg="#ecf0f1")

        # ================= HEADER =================
        header = tk.Frame(self, bg="#2c3e50", height=60)
        header.pack(fill="x")

        tk.Label(
            header,
            text="SMART AUTORISK - SIMULATION IA",
            bg="#2c3e50",
            fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=15)

        # ================= NOTEBOOK =================
        tabs = ttk.Notebook(self)
        tabs.pack(expand=True, fill="both", padx=15, pady=15)

        # =========================================================
        # ===================== PROFIL ============================
        # =========================================================
        tab_profil = ttk.Frame(tabs)
        tabs.add(tab_profil, text="👤 Profil")

        card = self._center_card(tab_profil)

        ttk.Label(card, text="Analyse du conducteur", style="Title.TLabel").pack(pady=10)

        form = self._form(card)

        self.age = self._field(form, "Âge", 0)
        self.sexe = self._combo(form, "Sexe", ["Femme", "Homme"], 1, 1)
        self.permis = self._field(form, "Permis (années)", 2)
        self.aptitude = self._combo(form, "Aptitude", ["Réduite", "Normale"], 1, 3)

        ttk.Button(
            card,
            text="Calculer profil",
            style="Accent.TButton",
            command=self.calcul_profil
        ).pack(pady=15)

        self.result_profil = ttk.Label(card, style="Result.TLabel", text="Résultat : ---")
        self.result_profil.pack(pady=10)

        # =========================================================
        # ===================== RISQUE ============================
        # =========================================================
        tab_risque = ttk.Frame(tabs)
        tabs.add(tab_risque, text="⚠️ Risque")

        card = self._center_card(tab_risque)

        ttk.Label(card, text="Évaluation du risque", style="Title.TLabel").pack(pady=10)

        form = self._form(card)

        self.profil_box = self._combo(form, "Profil", ["Prudent", "Normal", "Risqué"], 0, 0)
        self.mois = self._combo(form, "Mois", [f"Mois {i}" for i in range(1, 13)], 0, 1)

        self.puissance = self._field(form, "Puissance", 2)
        self.annee = self._field(form, "Année", 3)

        self.typev = self._combo(form, "Type", ["Moto", "Voiture"], 0, 4)
        self.saison = self._combo(form, "Saison", ["Pluvieux", "Sec"], 1, 5)
        self.periode = self._combo(form, "Période", ["Calme", "Fête", "Vacance"], 0, 6)

        self.taux = self._field(form, "Taux", 7, default="0.5")

        ttk.Button(
            card,
            text="Calculer risque",
            style="Accent.TButton",
            command=self.calcul_risque
        ).pack(pady=15)

        self.result_risque = ttk.Label(card, style="Result.TLabel", text="Résultat : ---")
        self.result_risque.pack(pady=10)

        # =========================================================
        # ====================== FRAIS ============================
        # =========================================================
        tab_frais = ttk.Frame(tabs)
        tabs.add(tab_frais, text="💰 Frais")

        card = self._center_card(tab_frais)

        ttk.Label(card, text="Calcul des frais", style="Title.TLabel").pack(pady=10)

        form = self._form(card)

        self.risque_box = self._combo(form, "Risque", ["Faible", "Moyen", "Élevé"], 0, 0)
        self.typev_frais = self._combo(form, "Type", ["Moto", "Voiture"], 0, 1)

        self.places = self._field(form, "Places", 2, default="2")
        self.usage = self._combo(form, "Usage", ["Personnel", "Transport"], 0, 3)
        self.tarif = self._combo(form, "Tarif", ["Simple", "Premium"], 0, 4)
        self.valeur = self._field(form, "Valeur", 5)

        ttk.Button(
            card,
            text="Calculer frais",
            style="Accent.TButton",
            command=self.calcul_frais
        ).pack(pady=15)

        self.result_frais = ttk.Label(card, style="Result.TLabel", text="Résultat : ---")
        self.result_frais.pack(pady=10)
        
    # ================= LOGIC =================

    def calcul_profil(self):
        age = float(self.age.get() or 0)
        sexe = self.sexe.current()
        permis = float(self.permis.get() or 0)
        aptitude = self.aptitude.current()

        x = [sexe, age / 100, permis / 50, aptitude]

        res = profil_model.predict(x)
        labels = ["Prudent", "Normal", "Risqué"]

        self.result_profil.config(text=labels[res])

    def calcul_risque(self):
        x = [
            self.profil_box.current() / 2,
            self.mois.current() / 12,
            float(self.puissance.get() or 0) / 400,
            1 - ((int(self.annee.get() or 2000) - 1800) / (2026 - 1800)),
            self.typev.current(),
            self.saison.current(),
            self.periode.current() / 2,
            float(self.taux.get() or 0)
        ]

        res = risque_model.predict(x)
        labels = ["Faible", "Moyen", "Élevé"]

        self.result_risque.config(text=labels[res])

    def calcul_frais(self):
        risque = self.risque_box.current() / 2
        typev = self.typev_frais.current()
        places = float(self.places.get() or 0) / 30
        usage = self.usage.current()
        tarif = self.tarif.current()
        valeur = float(self.valeur.get() or 0)

        if typev == 0:
            valeur /= 50000000
        else:
            valeur /= 100000000

        x = [risque, typev, places, usage, tarif, valeur]

        res = frais_model.predict(x)

        self.result_frais.config(text=f"{round(res,2)*1000} Ar")

    def _center_card(self, parent):
        frame = ttk.Frame(parent, style="Card.TFrame")
        frame.place(relx=0.5, rely=0.5, anchor="center", width=520)
        return frame


    def _form(self, parent):
        frame = ttk.Frame(parent, style="Card.TFrame")
        frame.pack(fill="x", padx=30, pady=10)
        return frame


    def _field(self, parent, label, row, default=""):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        entry = ttk.Entry(parent, width=30)
        entry.grid(row=row, column=1, pady=8)
        if default:
            entry.insert(0, default)
        return entry


    def _combo(self, parent, label, values, default, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        cb = ttk.Combobox(parent, values=values, width=28)
        cb.current(default)
        cb.grid(row=row, column=1, pady=8)
        return cb