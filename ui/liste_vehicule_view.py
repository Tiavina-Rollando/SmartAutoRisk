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
        self.configure(bg="#f2f4f8")

        # ================= STYLES TTK =================
        style = ttk.Style()
        style.theme_use("clam")

        # Style de l'en-tête du tableau
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 11, "bold"),
            background="#2c3e50",
            foreground="white",
            relief="flat"
        )
        style.map("Treeview.Heading", background=[('active', '#34495e')])

        # Style du corps du tableau (lignes plus hautes et texte plus grand)
        style.configure(
            "Treeview",
            font=("Segoe UI", 11),
            rowheight=32,
            background="white",
            fieldbackground="white",
            borderwidth=0
        )
        style.map("Treeview", background=[('selected', '#e8f0fe')], foreground=[('selected', '#1a73e8')])

        # ================= HEADER =================
        header = tk.Frame(self, bg="#2c3e50")
        header.pack(fill="x")

        tk.Label(
            header,
            text="SMART AUTORISK - VÉHICULES",
            bg="#2c3e50",
            fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=18)

        # ================= MAIN CONTAINER =================
        main_frame = tk.Frame(self, bg="#f2f4f8")
        main_frame.pack(fill="both", expand=True, padx=25, pady=20)

        # ================= CARD RECHERCHE =================
        card_search = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
        card_search.pack(fill="x", pady=(0, 20))

        search_inner = tk.Frame(card_search, bg="white", padx=20, pady=15)
        search_inner.pack(fill="x")

        # Labels et Comboboxes (Tailles augmentées)
        tk.Label(search_inner, text="Marque", bg="white", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(0, 5))
        tk.Label(search_inner, text="Modèle", bg="white", font=("Segoe UI", 11, "bold")).grid(row=0, column=1, sticky="w", padx=10, pady=(0, 5))
        tk.Label(search_inner, text="Année", bg="white", font=("Segoe UI", 11, "bold")).grid(row=0, column=2, sticky="w", padx=10, pady=(0, 5))

        self.marque_combo = ttk.Combobox(search_inner, width=22, font=("Segoe UI", 11))
        self.marque_combo.grid(row=1, column=0, padx=10, ipady=4)

        self.modele_combo = ttk.Combobox(search_inner, width=22, font=("Segoe UI", 11))
        self.modele_combo.grid(row=1, column=1, padx=10, ipady=4)

        self.annee_combo = ttk.Combobox(search_inner, width=22, font=("Segoe UI", 11))
        self.annee_combo.grid(row=1, column=2, padx=10, ipady=4)

        # Events
        self.marque_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())
        self.modele_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())
        self.annee_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        # Bouton Ajouter
        tk.Button(
            search_inner,
            text="➕ Ajouter",
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=18,
            pady=6,
            relief="flat",
            cursor="hand2",
            activebackground="#219150",
            activeforeground="white",
            command=self.ouvrir_form_ajout
        ).grid(row=1, column=3, padx=(20, 10))

        # Bouton Réinitialiser
        tk.Button(
            search_inner,
            text="🔄",
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=15,
            pady=6,
            relief="flat",
            cursor="hand2",
            activebackground="#c0392b",
            activeforeground="white",
            command=self.reset_filters
        ).grid(row=1, column=4, padx=5)

        # ================= CARD TABLEAU =================
        table_card = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
        table_card.pack(fill="both", expand=True)

        columns = ("Immatriculation", "Type", "Propriétaire", "Marque", "Modele", "Année", "Actions")

        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            self.tree.heading(col, text=col)
            width = 90 if col == "Actions" else 150
            self.tree.column(col, anchor="center", width=width)

        self.tree.pack(fill="both", expand=True, padx=15, pady=15)
        self.tree.bind("<Button-1>", self.on_click_tree)

        # Configurer l'alternance de couleur des lignes
        self.tree.tag_configure('oddrow', background='#f9fa00')
        self.tree.tag_configure('evenrow', background='white')

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
        marques = sorted(set(str(v[4]) for v in self.all_vehicules if v[4]))
        modeles = sorted(set(str(v[5]) for v in self.all_vehicules if v[5]))
        annees = sorted(set(str(v[6]) for v in self.all_vehicules if v[6]))

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