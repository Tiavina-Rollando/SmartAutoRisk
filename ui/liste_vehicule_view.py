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

        tk.Label(search, text="Marque", bg="white").grid(row=0, column=0)
        tk.Label(search, text="Modele", bg="white").grid(row=0, column=1)
        tk.Label(search, text="Année", bg="white").grid(row=0, column=2)

        self.marque_combo = ttk.Combobox(search, width=25)
        self.marque_combo.grid(row=1, column=0, padx=20)

        self.modele_combo = ttk.Combobox(search, width=25)
        self.modele_combo.grid(row=1, column=1, padx=20)

        self.annee_combo = ttk.Combobox(search, width=25)
        self.annee_combo.grid(row=1, column=2, padx=20)

        tk.Button(
            search,
            text="Rechercher",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            command=self.rechercher
        ).grid(row=1, column=3, padx=20)

        style = ttk.Style()
        style.theme_use("default")

        # ================= AJOUT =================
        tk.Button(
            search,
            text="Ajouter",
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            command=self.ouvrir_form_ajout
        ).grid(row=1, column=4, padx=10)
        
        # ===== HEADER =====
        style.configure(
            "Treeview.Heading",
            background="#bdc3c7",
            foreground="black",
            font=("Arial", 12, "bold")
        )

        # ===== TABLE =====
        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            rowheight=28,
            fieldbackground="white"
        )

        style.map(
            "Treeview",
            background=[("selected", "#3498db")],
            foreground=[("selected", "white")]
        )

        # ================= TABLE =================
        table_card = tk.Frame(main_frame, bg="white")
        table_card.pack(fill="both", expand=True, padx=40, pady=20)

        columns = ("Immatriculation", "Type", "Propriétaire", "Marque", "Modele", "Année", "Actions")

        self.tree = ttk.Treeview(table_card, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)

        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

        table_card.configure(bg="white", bd=1, relief="solid")
        # events
        self.tree.bind("<Button-1>", self.on_click_tree)

        self.charger()

    # ================= LOAD =================
    def charger(self):

        self.tree.delete(*self.tree.get_children())

        data = charger_vehicules()

        for row in data:
            vehicule_id = row[0]
            immatriculation = row[1]
            type = row[2]
            proprietaire = row[3]
            marque = row[4]
            modele = row[5]
            annee = row[6]
            self.tree.insert(
                "",
                "end",
                values=(immatriculation, type, proprietaire, marque, modele, annee, "🗑", vehicule_id)
            )

    # ================= CLICK =================
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
        imm = values[0]

        if column == "#1":  # Details
            self.ouvrir_detail(vehicule_id, imm)

        elif column == "#7":  # Supprimer
            self.supprimer_vehicule(vehicule_id, item)

    # ================= DELETE =================
    def supprimer_vehicule(self, vehicule_id, item):

        if messagebox.askyesno("Confirmation", "Supprimer ce véhicule ?"):
            supprimer_vehicule_db(vehicule_id)
            self.tree.delete(item)
            messagebox.showinfo("Succès", "Véhicule supprimé avec succès")
            self.refresh_table()

    # ================= DETAIL =================
    def ouvrir_detail(self, vehicule_id, immatriculation):

        from ui.detail_vehicule_view import DetailVehiculeView

        top = tk.Toplevel(self)
        DetailVehiculeView(top, vehicule_id, immatriculation)

    # ================= AJOUT =================
    def ouvrir_form_ajout(self):

        top = tk.Toplevel(self)
        top.title("Ajouter un membre")
        top.geometry("500x400")

        AjoutVehiculeView(top, refresh_callback=self.refresh_table)


    # ================= REFRESH =================
    def refresh_table(self):
        self.charger()

    # ============================= # RECHERCHE # ============================= 
    def rechercher(self): 
        marque_v = self.marque_combo.get() 
        modele_v = self.modele_combo.get() 
        annee_v = self.annee_combo.get() 
        # récupérer tous les items affichés 
        items = self.tree.get_children() 
        for item in items: 
            values = self.tree.item(item)["values"] 
            tags = self.tree.item(item)["tags"] 
            nom_tree = str(values[0]) 
            marque_tree = str(values[3]) 
            modele_tree = str(values[4]) 
            annee_tree = str(values[5]) 
            # Comparer critères (ignorer champs vides) 
            if ((not marque_v or marque_v == marque_tree) and (not modele_v or modele_v == modele_tree) and (not annee_v or annee_v == annee_tree)): 
                # supprimer ligne 
                self.tree.delete(item) 
                # remettre en première position 
                self.tree.insert("", 0, values=values,tags=tags) 
                break