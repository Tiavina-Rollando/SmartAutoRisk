import tkinter as tk
from tkinter import ttk, messagebox
from ui.insert_client_view import AjoutVehiculeView
from controllers.vehicule_controller import (
    charger_vehicules,
    supprimer_vehicule_db
)


class ListeVehiculeView(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

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
            text="SMART AUTORISK - VÉHICULES",
            bg="#2c3e50",
            fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=15)

        # ================= MAIN =================
        main_frame = tk.Frame(self, bg="#ecf0f1")
        main_frame.pack(fill="both", expand=True)

        # ================= SEARCH =================
        card = tk.Frame(main_frame, bg="white", height=120)
        card.pack(fill="x", padx=40)
        card.pack_propagate(False)

        search = tk.Frame(card, bg="white")
        search.pack(expand=True)

        # Labels
        tk.Label(search, text="Marque", bg="white").grid(row=0, column=0)
        tk.Label(search, text="Modele", bg="white").grid(row=0, column=1)
        tk.Label(search, text="Année", bg="white").grid(row=0, column=2)

        # Combobox
        self.marque_combo = ttk.Combobox(search, width=25)
        self.marque_combo.grid(row=1, column=0, padx=20)

        self.modele_combo = ttk.Combobox(search, width=25)
        self.modele_combo.grid(row=1, column=1, padx=20)

        self.annee_combo = ttk.Combobox(search, width=25)
        self.annee_combo.grid(row=1, column=2, padx=20)

        # Events (un seul moteur)
        self.marque_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())
        self.modele_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())
        self.annee_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        # Bouton reset
        tk.Button(
            search,
            text="🔄",
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            command=self.reset_filters
        ).grid(row=1, column=5, padx=10)

        # Bouton ajouter
        tk.Button(
            search,
            text="Ajouter",
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            command=self.ouvrir_form_ajout
        ).grid(row=1, column=4, padx=10)

        # ================= TABLE =================
        table_card = tk.Frame(main_frame, bg="white")
        table_card.pack(fill="both", expand=True, padx=40, pady=20)

        columns = ("Immatriculation", "Type", "Propriétaire", "Marque", "Modele", "Année", "Actions")

        self.tree = ttk.Treeview(table_card, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)

        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

        self.tree.bind("<Button-1>", self.on_click_tree)

        # ================= DATA SOURCE =================
        self.all_vehicules = charger_vehicules()
        self.init_combobox_values()
        self.apply_filter()

    # ================= LOAD TREE =================
    def charger(self):
        self.tree.delete(*self.tree.get_children())

        for row in self.all_vehicules:
            self.tree.insert(
                "",
                "end",
                values=(row[1], row[2], row[3], row[4], row[5], row[6], "🗑", row[0])
            )

    # ================= FILTER =================
    def apply_filter(self):

        marque = self.marque_combo.get().lower()
        modele = self.modele_combo.get().lower()
        annee = self.annee_combo.get().lower()

        self.tree.delete(*self.tree.get_children())

        for row in self.all_vehicules:

            if (
                (not marque or marque in str(row[4]).lower()) and
                (not modele or modele in str(row[5]).lower()) and
                (not annee or annee in str(row[6]).lower())
            ):
                self.tree.insert(
                    "",
                    "end",
                    values=(row[1], row[2], row[3], row[4], row[5], row[6], "🗑", row[0])
                )

    # ================= RESET =================
    def reset_filters(self):
        self.marque_combo.set("")
        self.modele_combo.set("")
        self.annee_combo.set("")
        self.apply_filter()

    # ================= INIT COMBO =================
    def init_combobox_values(self):

        marques = sorted(set(str(v[4]) for v in self.all_vehicules))
        modeles = sorted(set(str(v[5]) for v in self.all_vehicules))
        annees = sorted(set(str(v[6]) for v in self.all_vehicules))

        self.marque_combo["values"] = marques
        self.modele_combo["values"] = modeles
        self.annee_combo["values"] = annees

    # ================= DELETE =================
    def supprimer_vehicule(self, vehicule_id):

        if messagebox.askyesno("Confirmation", "Supprimer ce véhicule ?"):
            supprimer_vehicule_db(vehicule_id)
            messagebox.showinfo("Succès", "Véhicule supprimé avec succès")
            self.all_vehicules = charger_vehicules()
            self.init_combobox_values()
            self.apply_filter()

    # ================= DETAIL =================
    def ouvrir_detail(self, vehicule_id, immatriculation):
        from ui.detail_vehicule_view import DetailVehiculeView

        top = tk.Toplevel(self)
        DetailVehiculeView(top, vehicule_id, immatriculation)

    # ================= AJOUT =================
    def ouvrir_form_ajout(self):

        top = tk.Toplevel(self)
        top.title("Ajouter un véhicule")
        top.geometry("500x400")

        AjoutVehiculeView(top, refresh_callback=self.reload_data)

    # ================= REFRESH GLOBAL =================
    def reload_data(self):
        self.all_vehicules = charger_vehicules()
        self.init_combobox_values()
        self.apply_filter()

    # ================= CLICK TREE =================
    def on_click_tree(self, event):

        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)

        if not item:
            return

        values = self.tree.item(item, "values")
        vehicule_id = values[7]
        print(f"Clicked on column {column} for vehicule ID {vehicule_id}")

        if column == "#1":
            self.ouvrir_detail(vehicule_id, values[0])

        elif column == "#7":
            self.supprimer_vehicule(vehicule_id)