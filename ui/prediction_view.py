from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from database.models.accident import Accident
from database.models.accident_vehicule import AccidentVehicule
from database.models.base import get_session
from database.models.vehicule import Vehicule
from RNA_PROFIL.rna_profil import NeuralNetwork as ProfilNN
from RNA_RATE.rna_rate import NeuralNetwork as FeeNN
from RNA_RISK.rna_risk import NeuralNetwork as RiskNN
from services.poisson_service import predire_accidents_poisson


def determiner_saison(date_obj):
  """
    Détermine la période/saison incluant la météo, 
    les vacances et les périodes de fête (contexte de Madagascar).
    """
  if not date_obj:
    return "Saison sèche"

  mois = date_obj.month
  jour = date_obj.day

  # 1. Périodes de Fêtes majeures (ex: Fin d'année / Noël / Nouvel An / Fête Nationale)
  if (mois == 12 and jour >= 20) or (mois == 1 and jour <= 5):
    return "Période de Fêtes"
  if mois == 6 and (20 <= jour <= 30):
    return "Période de Fêtes"

  # 2. Périodes de Vacances scolaires / estivales (ex: Juillet - Septembre)
  elif mois in [7, 8, 9]:
    return "Période de Vacances"

  # 3. Saisons climatiques habituelles
  elif mois in [11, 12, 1, 2, 3, 4]:
    return "Saison des pluies"
  else:
    return "Saison sèche"


def evaluer_risque_stochastique(
    accidents_vehicule, saison_cible, moyenne_flotte=1.0
):
  accidents_saison = [
      acc
      for acc in accidents_vehicule
      if acc.date and determiner_saison(acc.date) == saison_cible
  ]
  lambda_vehicule = len(accidents_saison)
  ratio = (
      lambda_vehicule / moyenne_flotte
      if moyenne_flotte > 0
      else lambda_vehicule
  )

  if ratio > 1.5:
    return "Élevé", ratio
  elif ratio >= 0.8:
    return "Modéré", ratio
  else:
    return "Faible", ratio


# ================= MODELS =================
profil_model = ProfilNN(4, 5, 3)
profil_model.load_model("models/profil_model.json")

risque_model = RiskNN(8, 10, 3)
risque_model.load_model("models/risk_model.json")

frais_model = FeeNN(6, 6)
frais_model.load_model("models/rate_model.json")


# VIEW
class Prediction(tk.Frame):

  def __init__(self, parent):
    super().__init__(parent)

    # STYLE
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TLabel", background="white")
    style.configure("TFrame", background="white")
    style.configure("Card.TFrame", background="white")
    style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
    style.configure("Sub.TLabel", font=("Segoe UI", 11))
    style.configure(
        "Result.TLabel", font=("Segoe UI", 11, "bold"), foreground="#1f3a93"
    )
    style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))

    # BACKGROUND
    self.configure(bg="#ecf0f1")

    # HEADER
    header = tk.Frame(self, bg="#2c3e50", height=60)
    header.pack(fill="x")

    tk.Label(
        header,
        text="SMART AUTORISK - SIMULATION IA",
        bg="#2c3e50",
        fg="white",
        font=("Segoe UI", 16, "bold"),
    ).pack(pady=15)

    # NOTEBOOK
    tabs = ttk.Notebook(self)
    tabs.pack(expand=True, fill="both", padx=15, pady=15)

    # PROFIL
    tab_profil = ttk.Frame(tabs)
    tabs.add(tab_profil, text="👤 Profil")
    card = self._center_card(tab_profil)
    ttk.Label(card, text="Analyse du conducteur", style="Title.TLabel").pack(
        pady=10
    )

    form = self._form(card)

    self.age = self._field(form, "Âge", 0)
    self.sexe = self._combo(form, "Sexe", ["Femme", "Homme"], 1, 1)
    self.permis = self._field(form, "Permis (années)", 2)
    self.aptitude = self._combo(form, "Aptitude", ["Réduite", "Normale"], 1, 3)

    ttk.Button(
        card,
        text="Calculer profil",
        style="Accent.TButton",
        command=self.calcul_profil,
    ).pack(pady=15)

    self.result_profil = ttk.Label(
        card, style="Result.TLabel", text="Résultat : ---"
    )
    self.result_profil.pack(pady=10)

    # RISQUE
    tab_risque = ttk.Frame(tabs)
    tabs.add(tab_risque, text="⚠️ Risque")

    card = self._center_card(tab_risque)

    ttk.Label(card, text="Évaluation du risque", style="Title.TLabel").pack(
        pady=10
    )

    form = self._form(card)

    self.profil_box = self._combo(
        form, "Profil", ["Prudent", "Normal", "Risqué"], 0, 0
    )
    self.mois = self._combo(
        form, "Mois", [f"Mois {i}" for i in range(1, 13)], 0, 1
    )

    self.puissance = self._field(form, "Puissance", 2)
    self.annee = self._field(form, "Année", 3)

    self.typev = self._combo(form, "Type", ["Moto", "Voiture"], 0, 4)
    self.saison = self._combo(form, "Saison", ["Pluvieux", "Sec"], 1, 5)
    self.periode = self._combo(
        form, "Période", ["Calme", "Fête", "Vacance"], 0, 6
    )

    self.taux = self._field(form, "Taux", 7, default="0.5")

    ttk.Button(
        card,
        text="Calculer risque",
        style="Accent.TButton",
        command=self.calcul_risque,
    ).pack(pady=15)

    self.result_risque = ttk.Label(
        card, style="Result.TLabel", text="Résultat : ---"
    )
    self.result_risque.pack(pady=10)

    #  FRAIS
    tab_frais = ttk.Frame(tabs)
    tabs.add(tab_frais, text="💰 Frais")
    card = self._center_card(tab_frais)
    ttk.Label(card, text="Calcul des frais", style="Title.TLabel").pack(pady=10)
    form = self._form(card)
    self.risque_box = self._combo(
        form, "Risque", ["Faible", "Moyen", "Élevé"], 0, 0
    )
    self.typev_frais = self._combo(form, "Type", ["Moto", "Voiture"], 0, 1)
    self.places = self._field(form, "Places", 2, default="2")
    self.usage = self._combo(form, "Usage", ["Personnel", "Transport"], 0, 3)
    self.tarif = self._combo(form, "Tarif", ["Simple", "Premium"], 0, 4)
    self.valeur = self._field(form, "Valeur", 5)

    ttk.Button(
        card,
        text="Calculer frais",
        style="Accent.TButton",
        command=self.calcul_frais,
    ).pack(pady=15)
    self.result_frais = ttk.Label(
        card, style="Result.TLabel", text="Résultat : ---"
    )
    self.result_frais.pack(pady=10)

    # POISSON
    tab_poisson = ttk.Frame(tabs)
    tabs.add(tab_poisson, text="📈 Poisson & Risque Saisonnier")

    card_poisson = self._center_card(tab_poisson)

    ttk.Label(
        card_poisson,
        text="Processus Stochastique & Risque par Saison",
        style="Title.TLabel",
    ).pack(pady=10)

    form_poisson = self._form(card_poisson)

    # Sélection du véhicule
    ttk.Label(form_poisson, text="Véhicule").grid(
        row=0, column=0, sticky="w", padx=10, pady=8
    )
    self.cb_vehicule_poisson = ttk.Combobox(
        form_poisson, width=28, state="readonly"
    )
    self.cb_vehicule_poisson.grid(row=0, column=1, pady=8)
    self.charger_liste_vehicules_poisson()

    # Horizon en mois
    self.poisson_horizon_mois = self._field(
        form_poisson, "Horizon (mois)", 1, default="12"
    )

    btn_row = ttk.Frame(card_poisson, style="Card.TFrame")
    btn_row.pack(pady=10)

    ttk.Button(
        btn_row,
        text="Simuler Poisson",
        style="Accent.TButton",
        command=self.calcul_poisson,
    ).pack(side="left", padx=5)

    ttk.Button(
        btn_row,
        text="Calculer Risque par Saison",
        style="Accent.TButton",
        command=self.calculer_risque_stochastique_saison,
    ).pack(side="left", padx=5)

    self.result_poisson = ttk.Label(
        card_poisson,
        style="Result.TLabel",
        text="Prévision en attente de calcul...",
        justify="left",
    )
    self.result_poisson.pack(pady=8)

    # Conteneur sous forme de liste/blocs (remplace le tableau Treeview)
    self.container_resultats_saison = ttk.Frame(
        card_poisson, style="Card.TFrame"
    )
    self.container_resultats_saison.pack(
        pady=10, fill="x", padx=20, expand=True
    )

  # LOGIC 
  def charger_liste_vehicules_poisson(self):
    session = get_session()
    try:
      vehicules = session.query(Vehicule).all()
      self.cb_vehicule_poisson["values"] = [
          f"{v.id} — {getattr(v, 'immatriculation', '')} ({getattr(v, 'marque', '')} {getattr(v, 'modele', '')})"
          for v in vehicules
      ]
      if self.cb_vehicule_poisson["values"]:
        self.cb_vehicule_poisson.current(0)
    except Exception as e:
      pass
    finally:
      session.close()

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
        float(self.taux.get() or 0),
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

  def calcul_poisson(self):
    selection = self.cb_vehicule_poisson.get()
    if not selection:
      messagebox.showwarning("Attention", "Veuillez sélectionner un véhicule.")
      return
    try:
      vehicule_id = int(selection.split(" — ")[0].strip())
      horizon_mois = float(self.poisson_horizon_mois.get().strip() or 12.0)
      horizon_annees = horizon_mois / 12.0
      session = get_session()
      try:
        res = predire_accidents_poisson(
            session, vehicule_id, horizon_annees=horizon_annees
        )
        nb_accidents = res["prediction_accidents_futurs"]
        prob_zero = res["probabilite_aucun_accident"]

        texte_resultat = (
            f"📊 Prévision sur {int(horizon_mois)} mois :\n"
            f"• Nombre estimé d'accidents : {nb_accidents}\n"
            f"• Probabilité de 0 accident : {prob_zero}%"
        )
        self.result_poisson.config(
            text=texte_resultat,
            justify="left",
            font=("Segoe UI", 11, "bold"),
            foreground="#1f3a93",
        )
      finally:
        session.close()
    except ValueError:
      messagebox.showwarning(
          "Valeur invalide",
          "Veuillez entrer un nombre de mois valide.",
      )
    except Exception as e:
      messagebox.showerror("Erreur", str(e))
      
  def calculer_risque_stochastique_saison(self):
    selection = self.cb_vehicule_poisson.get()
    if not selection:
      messagebox.showwarning("Attention", "Veuillez sélectionner un véhicule.")
      return

    vehicule_id = int(selection.split(" — ")[0].strip())

    session = get_session()
    try:
      accidents_vehicule = (
          session.query(Accident)
          .join(Accident.vehicules)
          .filter(AccidentVehicule.vehicule_id == vehicule_id)
          .all()
      )

      moyenne_flotte = 1.0

      # 4 catégories analysées (saisons + fêtes + vacances)
      categories = [
          "Saison des pluies",
          "Saison sèche",
          "Période de Fêtes",
          "Période de Vacances",
      ]

      # Nettoyer les anciens blocs
      for widget in self.container_resultats_saison.winfo_children():
        widget.destroy()

      # En-tête de section lisible
      ttk.Label(
          self.container_resultats_saison,
          text="Analyse du risque par période :",
          font=("Segoe UI", 11, "bold"),
          foreground="#2c3e50",
      ).pack(anchor="w", pady=(0, 6))

      # Affichage sous forme de lignes de texte claires et aérées
      for cat in categories:
        acc_cat = [
            acc
            for acc in accidents_vehicule
            if acc.date and determiner_saison(acc.date) == cat
        ]
        nb_acc = len(acc_cat)
        niveau, ratio = evaluer_risque_stochastique(
            accidents_vehicule, cat, moyenne_flotte
        )

        # Choix de la couleur selon le niveau de risque pour plus de lisibilité
        couleur_texte = "#2c3e50"
        if niveau == "Élevé":
          couleur_texte = "#c0392b"  # Rouge
        elif niveau == "Modéré":
          couleur_texte = "#d35400"  # Orange
        else:
          couleur_texte = "#27ae60"  # Vert

        ligne_texte = (
            f"• {cat} :  {nb_acc} accident(s)  |  "
            f"Risque : {niveau}  (Indice : {ratio:.2f})"
        )

        lbl = ttk.Label(
            self.container_resultats_saison,
            text=ligne_texte,
            font=("Segoe UI", 10),
            foreground=couleur_texte,
        )
        lbl.pack(anchor="w", pady=2, fill="x")

    except Exception as e:
      messagebox.showerror("Erreur", f"Erreur calcul par période : {e}")
    finally:
      session.close()

  def _center_card(self, parent):
    frame = ttk.Frame(parent, style="Card.TFrame")
    frame.place(relx=0.5, rely=0.5, anchor="center", width=540)
    return frame

  def _form(self, parent):
    frame = ttk.Frame(parent, style="Card.TFrame")
    frame.pack(fill="x", padx=30, pady=10)
    return frame

  def _field(self, parent, label, row, default=""):
    ttk.Label(parent, text=label).grid(
        row=row, column=0, sticky="w", padx=10, pady=8
    )
    entry = ttk.Entry(parent, width=30)
    entry.grid(row=row, column=1, pady=8)
    if default:
      entry.insert(0, default)
    return entry

  def _combo(self, parent, label, values, default, row):
    ttk.Label(parent, text=label).grid(
        row=row, column=0, sticky="w", padx=10, pady=8
    )
    cb = ttk.Combobox(parent, values=values, width=28)
    cb.current(default)
    cb.grid(row=row, column=1, pady=8)
    return cb