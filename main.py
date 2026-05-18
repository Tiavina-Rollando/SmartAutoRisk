import tkinter as tk
from tkinter import ttk
from datetime import datetime
import locale
from tkinter import font
from PIL import Image, ImageTk
import database.models.all_models as models

# ===== IMPORT TES PAGES =====
from ui.dashboard_view import Dashboard
from ui.liste_vehicule_view import ListeVehiculeView as Vehicules
from ui.accident_view import Accidents
from ui.prediction_view import Prediction


# ================= APP PRINCIPALE =================

class App:

    def __init__(self, root):

        self.root = root
        self.root.title("SmartAutoRisk")
        self.root.geometry("1200x700")

        # ---------- LAYOUT PRINCIPAL ----------
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # ---------- SIDEBAR ----------
        self.menu_frame = tk.Frame(self.main_frame, bg="#2c3e50", width=220)
        self.menu_frame.pack(side="left", fill="y")
        
        # ---------- LOGO ----------
        image = Image.open('assets/ISPM1.png')
        image = image.resize((100,100))

        self.logo = ImageTk.PhotoImage(image)
        logo_label = tk.Label(
            self.menu_frame,
            image = self.logo,
            bg = "#2c3e50"
        )
        logo_label.pack(pady=10)

        tk.Label(
            self.menu_frame,
            text="Menu",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 30, "bold")
        ).pack(pady=20)

        # ================= DATE DANS SIDEBAR =================
        self.date_label = tk.Label(
            self.menu_frame,
            text="",
            bg="#2c3e50",
            fg="#ecf0f1",
            font=("Arial", 14, "bold")
        )
        self.date_label.pack(pady=10)

        # ---------- CONTENU DROITE ----------
        self.container = tk.Frame(self.main_frame)
        self.container.pack(side="right", fill="both", expand=True)

        # ---------- PAGES ----------
        self.frames = {}

        for Page in (Dashboard, Vehicules, Prediction):
            frame = Page(self.container)
            self.frames[Page] = frame
            frame.place(relwidth=1, relheight=1)

        # ---------- MENU ----------
        self.buttons = []
        self.create_sidebar()

        # Page par défaut
        self.show_frame(Dashboard)

        # ================= START CLOCK =================
        try:
            locale.setlocale(locale.LC_TIME, "fr_FR")
        except:
            locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
            
        self.update_date()

    # ================= DATE UPDATE =================
    def update_date(self):
        now = datetime.now()
        formatted = now.strftime("%A %d %B %Y - %H:%M:%S")
        self.date_label.config(text=formatted)

        # mise à jour chaque seconde
        self.root.after(1000, self.update_date)

    # ================= SIDEBAR =================
    def create_sidebar(self):

        menu_buttons = [
            ("Tableau de bord", Dashboard),
            ("Véhicules", Vehicules),
            ("Prédiction", Prediction)
        ]

        for text, page in menu_buttons:

            btn = tk.Button(
                self.menu_frame,
                text=text,
                bg="#34495e",
                fg="white",
                font=("Arial", 16),
                relief="flat",
                width=20,
                height=2,
                cursor="hand2",
                command=lambda p=page, b=None: self.change_page(p, b)
            )

            btn.pack(pady=5)
            self.buttons.append(btn)

    # ================= NAVIGATION =================
    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()

    def change_page(self, page, btn):
        self.show_frame(page)

        # Reset couleur boutons
        for b in self.buttons:
            b.config(bg="#34495e")

        # Highlight actif
        if btn:
            btn.config(bg="#1abc9c")


# ================= RUN =================

if __name__ == "__main__":

    root = tk.Tk()
    # ================= FONTES GLOBALES =================

    default_font = ("Arial", 14)

    # widgets tkinter classiques
    root.option_add("*Font", default_font)

    style = ttk.Style()

    # ttk widgets
    style.configure(".", font=default_font)

    # Treeview
    style.configure(
        "Treeview",
        font=("Arial", 14),
        rowheight=32
    )

    style.configure(
        "Treeview.Heading",
        font=("Arial", 16, "bold")
    )

    # Boutons
    style.configure(
        "TButton",
        font=("Arial", 14, "bold")
    )

    # Combobox
    style.configure(
        "TCombobox",
        font=("Arial", 14)
    )

    # LabelFrame
    style.configure(
        "TLabelframe.Label",
        font=("Arial", 16, "bold")
    )
    app = App(root)
    root.mainloop()