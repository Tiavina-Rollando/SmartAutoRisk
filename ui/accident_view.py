import base64
import json
import os
import io
import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from database.models.accident import Accident, GraviteEnum
from database.models.accident_vehicule import AccidentVehicule
from database.models.base import get_session
from database.models.vehicule import Vehicule


class FenetrePleinEcran(tk.Toplevel):
    """Fenêtre Pop-up affichant une image en très grand format / plein écran."""
    def __init__(self, parent, pil_image):
        super().__init__(parent)
        self.title("🔍 Visualisation Plein Écran")
        self.configure(bg="#000000")
        
        # Passer la fenêtre en mode plein écran / maximisée
        self.attributes("-fullscreen", True)

        self.pil_image = pil_image
        self.tk_image = None

        # Zone d'affichage de l'image
        self.lbl_image = tk.Label(self, bg="#000000", cursor="hand2")
        self.lbl_image.pack(fill="both", expand=True)

        # Bouton de fermeture en haut à droite
        btn_fermer = tk.Button(
            self, text="❌ Fermer (ou Échap)", command=self.destroy,
            bg="#EF4444", fg="white", font=("Segoe UI", 11, "bold"),
            relief="flat", cursor="hand2", padx=15, pady=6
        )
        btn_fermer.place(relx=0.98, rely=0.02, anchor="ne")

        # Raccourcis pour fermer la fenêtre
        self.bind("<Escape>", lambda e: self.destroy())
        self.lbl_image.bind("<Button-1>", lambda e: self.destroy())

        # Redimensionnement automatique lors de l'ouverture
        self.bind("<Configure>", self.redimensionner_image)

    def redimensionner_image(self, event=None):
        if not self.pil_image:
            return

        win_w = self.winfo_width()
        win_h = self.winfo_height()

        if win_w < 10 or win_h < 10:
            return

        # Copie et redimensionnement avec conservation du ratio
        img_copy = self.pil_image.copy()
        img_copy.thumbnail((win_w, win_h), Image.Resampling.LANCZOS)
        
        self.tk_image = ImageTk.PhotoImage(img_copy)
        self.lbl_image.config(image=self.tk_image)


class FenetreDetailsAccident(tk.Toplevel):
    """Fenêtre Pop-up d'informations détaillées sur un accident avec visionneuse de photos."""
    def __init__(self, parent, data):
        super().__init__(parent)
        self.title(f"Détails Accident N°{data['id']}")
        self.geometry("620x750")
        self.configure(bg="#F8FAFC")
        self.resizable(False, False)

        self.photos = data.get("raw_photos", [])
        self.current_photo_idx = 0
        self.tk_images = []
        self.current_pil_image = None

        # En-tête
        header = tk.Frame(self, bg="#0F172A", height=60)
        header.pack(fill="x")
        tk.Label(
            header, text=f"FICHE ACCIDENT N°{data['id']}", 
            bg="#0F172A", fg="#38BDF8", font=("Segoe UI", 16, "bold")
        ).pack(pady=15)

        container = tk.Frame(self, bg="#F8FAFC", padx=25, pady=10)
        container.pack(fill="both", expand=True)

        def ajouter_section(titre):
            lbl = tk.Label(container, text=titre, font=("Segoe UI", 11, "bold"), fg="#2563EB", bg="#F8FAFC", anchor="w")
            lbl.pack(fill="x", pady=(8, 2))

        def ajouter_ligne(label, valeur):
            f = tk.Frame(container, bg="#F8FAFC")
            f.pack(fill="x", pady=1)
            tk.Label(f, text=label + " :", font=("Segoe UI", 9, "bold"), bg="#F8FAFC", fg="#475569", width=22, anchor="w").pack(side="left")
            tk.Label(f, text=valeur, font=("Segoe UI", 9), bg="#F8FAFC", fg="#0F172A", anchor="w").pack(side="left")

        # 1. Synthèse générale
        ajouter_section("📍 Informations Générales")
        ajouter_ligne("Date de l'incident", data.get("date", "N/A"))
        ajouter_ligne("Lieu", data.get("lieu", "N/A"))
        ajouter_ligne("Niveau de gravité", data.get("gravite", "N/A"))
        ajouter_ligne("Type d'accident", data.get("type", "N/A"))

        # 2. Implication Véhicule & Dégâts
        ajouter_section("🚗 Véhicule & Constatations")
        ajouter_ligne("Véhicule(s) impliqué(s)", data.get("vehicule", "N/A"))
        ajouter_ligne("Niveau de dégât", data.get("degat", "N/A"))
        ajouter_ligne("Responsabilité engagée", data.get("responsabilite", "N/A"))
        ajouter_ligne("Estimation dégâts", f"{data.get('valeur', '0')} Ar")

        # 3. Section Visionneuse de Photos
        ajouter_section(f"📷 Documents Visuels ({len(self.photos)}) — Clic pour Agrandir")
        
        photo_box = tk.Frame(container, bg="#0F172A", height=220)
        photo_box.pack(fill="x", pady=5)

        self.lbl_photo_viewer = tk.Label(
            photo_box, bg="#0F172A", fg="#94A3B8",
            text="Aucune photo disponible" if not self.photos else "",
            font=("Segoe UI", 10), cursor="hand2" if self.photos else "arrow"
        )
        self.lbl_photo_viewer.pack(fill="both", expand=True)

        # Clic sur l'image pour l'ouvrir en plein écran
        self.lbl_photo_viewer.bind("<Button-1>", self.ouvrir_plein_ecran)

        if self.photos:
            nav_bar = tk.Frame(container, bg="#1E293B")
            nav_bar.pack(fill="x", pady=(2, 5))

            tk.Button(
                nav_bar, text="◀ Précédent", command=self.photo_prev,
                bg="#EF4444", fg="white", font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2", padx=6
            ).pack(side="left", padx=5, pady=3)

            self.lbl_counter = tk.Label(nav_bar, text="", bg="#1E293B", fg="white", font=("Segoe UI", 9, "bold"))
            self.lbl_counter.pack(side="left", expand=True)

            tk.Button(
                nav_bar, text="Suivant ▶", command=self.photo_next,
                bg="#10B981", fg="white", font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2", padx=6
            ).pack(side="right", padx=5, pady=3)

            self.thumb_frame = tk.Frame(container, bg="#F8FAFC")
            self.thumb_frame.pack(fill="x", pady=2)

            self.afficher_photo_courante()

        tk.Button(
            self, text="Fermer", command=self.destroy,
            bg="#0F172A", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=25, pady=5, cursor="hand2"
        ).pack(pady=10)

    def charger_image_pil(self, photo_str):
        """Décode du Base64 ou charge un fichier local."""
        try:
            if photo_str.startswith("data:image") or len(photo_str) > 300:
                img_data = base64.b64decode(photo_str)
                return Image.open(io.BytesIO(img_data))
            elif os.path.exists(photo_str):
                return Image.open(photo_str)
        except Exception:
            pass
        return None

    def afficher_photo_courante(self):
        if not self.photos:
            return

        total = len(self.photos)
        self.lbl_counter.config(text=f"{self.current_photo_idx + 1} / {total}")

        raw_photo = self.photos[self.current_photo_idx]
        self.current_pil_image = self.charger_image_pil(raw_photo)

        if self.current_pil_image:
            img_disp = self.current_pil_image.copy()
            img_disp.thumbnail((380, 200), Image.Resampling.LANCZOS)
            photo_tk = ImageTk.PhotoImage(img_disp)
            self.tk_images.append(photo_tk)
            self.lbl_photo_viewer.config(image=photo_tk, text="")
        else:
            self.lbl_photo_viewer.config(image="", text="⚠️ Erreur de chargement de l'image")

        for widget in self.thumb_frame.winfo_children():
            widget.destroy()

        for i, p_str in enumerate(self.photos):
            t_img = self.charger_image_pil(p_str)
            if t_img:
                t_img = t_img.resize((35, 35), Image.Resampling.LANCZOS)
                t_tk = ImageTk.PhotoImage(t_img)
                self.tk_images.append(t_tk)

                border_col = "#2563EB" if i == self.current_photo_idx else "#CBD5E1"
                lbl = tk.Label(self.thumb_frame, image=t_tk, bd=2, relief="solid", bg=border_col, cursor="hand2")
                lbl.pack(side="left", padx=2)
                lbl.bind("<Button-1>", lambda e, idx=i: self.sauter_photo(idx))

    def ouvrir_plein_ecran(self, event=None):
        if self.current_pil_image:
            FenetrePleinEcran(self, self.current_pil_image)

    def photo_prev(self):
        if self.photos:
            self.current_photo_idx = (self.current_photo_idx - 1) % len(self.photos)
            self.afficher_photo_courante()

    def photo_next(self):
        if self.photos:
            self.current_photo_idx = (self.current_photo_idx + 1) % len(self.photos)
            self.afficher_photo_courante()

    def sauter_photo(self, idx):
        self.current_photo_idx = idx
        self.afficher_photo_courante()


class Accidents(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#F8FAFC")
        self.photos_selected_paths = []
        self.current_index = 0
        self.tk_images = []
        self.accidents_cache = {}

        self.configurer_styles_ttk()

        # =========================================================
        # EN-TÊTE PRINCIPAL
        # =========================================================
        header = tk.Frame(self, bg="#0F172A", height=70)
        header.pack(fill="x")

        tk.Label(
            header,
            text="SMART AUTORISK — GESTION DES ACCIDENTS",
            bg="#0F172A",
            fg="#38BDF8",
            font=("Segoe UI", 18, "bold"),
        ).pack(side="left", padx=25, pady=18)

        self.btn_action = tk.Button(
            header,
            text="➕ Ajouter un accident",
            bg="#10B981",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=8,
            activebackground="#059669",
            activeforeground="white",
            command=self.basculer_vers_ajout,
        )
        self.btn_action.pack(side="right", padx=25, pady=15)

        # =========================================================
        # CONTENEUR CENTRAL
        # =========================================================
        self.content_frame = tk.Frame(self, bg="#F8FAFC")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.creer_vue_liste()
        self.creer_vue_formulaire()

        self.afficher_vue_liste()

    def configurer_styles_ttk(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Custom.Treeview",
            font=("Segoe UI", 11),
            rowheight=32,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground="#0F172A",
            borderwidth=0,
        )
        style.configure(
            "Custom.Treeview.Heading",
            font=("Segoe UI", 11, "bold"),
            background="#1E293B",
            foreground="#FFFFFF",
            relief="flat",
        )
        style.map("Custom.Treeview.Heading", background=[("active", "#334155")])

        style.configure("TCombobox", font=("Segoe UI", 11), padding=5)
        style.configure("TEntry", font=("Segoe UI", 11), padding=5)

    # =========================================================
    # VUE 1 : LISTE DES ACCIDENTS (TREEVIEW + BARRE D'ACTIONS)
    # =========================================================
    def creer_vue_liste(self):
        self.frame_liste = tk.Frame(self.content_frame, bg="#F8FAFC")

        top_bar = tk.Frame(self.frame_liste, bg="#F8FAFC")
        top_bar.pack(fill="x", pady=(0, 15))

        tk.Label(
            top_bar,
            text="Liste des accidents enregistrés",
            font=("Segoe UI", 14, "bold"),
            fg="#0F172A",
            bg="#F8FAFC",
        ).pack(side="left")

        tk.Button(
            top_bar,
            text="🔄 Actualiser",
            command=self.charger_liste_accidents,
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            activebackground="#1D4ED8",
            activeforeground="white",
        ).pack(side="right")

        card_table = tk.Frame(
            self.frame_liste,
            bg="white",
            highlightbackground="#CBD5E1",
            highlightthickness=1,
        )
        card_table.pack(fill="both", expand=True)

        columns = (
            "id",
            "date",
            "vehicule",
            "lieu",
            "gravite",
            "type",
            "degat",
            "responsabilite",
            "valeur",
            "photos",
        )
        self.tree_accidents = ttk.Treeview(
            card_table, columns=columns, show="headings", style="Custom.Treeview"
        )

        self.tree_accidents.heading("id", text="ID")
        self.tree_accidents.heading("date", text="Date")
        self.tree_accidents.heading("vehicule", text="Véhicule")
        self.tree_accidents.heading("lieu", text="Lieu")
        self.tree_accidents.heading("gravite", text="Gravité")
        self.tree_accidents.heading("type", text="Type")
        self.tree_accidents.heading("degat", text="Dégât")
        self.tree_accidents.heading("responsabilite", text="Resp.")
        self.tree_accidents.heading("valeur", text="Valeur (Ar)")
        self.tree_accidents.heading("photos", text="Photos")

        self.tree_accidents.column("id", width=50, anchor="center")
        self.tree_accidents.column("date", width=100, anchor="center")
        self.tree_accidents.column("vehicule", width=180, anchor="w")
        self.tree_accidents.column("lieu", width=160, anchor="w")
        self.tree_accidents.column("gravite", width=90, anchor="center")
        self.tree_accidents.column("type", width=90, anchor="center")
        self.tree_accidents.column("degat", width=80, anchor="center")
        self.tree_accidents.column("responsabilite", width=70, anchor="center")
        self.tree_accidents.column("valeur", width=110, anchor="e")
        self.tree_accidents.column("photos", width=70, anchor="center")

        scrollbar = ttk.Scrollbar(
            card_table, orient="vertical", command=self.tree_accidents.yview
        )
        self.tree_accidents.configure(yscrollcommand=scrollbar.set)

        self.tree_accidents.pack(
            side="left", fill="both", expand=True, padx=2, pady=2
        )
        scrollbar.pack(side="right", fill="y", pady=2)

        self.tree_accidents.bind("<Double-1>", self.afficher_details_accident)

        frame_btn = tk.Frame(self.frame_liste, bg="#F8FAFC")
        frame_btn.pack(fill="x", pady=(15, 0))

        tk.Button(
            frame_btn,
            text="🔍 Infos Détaillées",
            command=self.afficher_details_accident,
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=7,
            activebackground="#1D4ED8",
            activeforeground="white",
        ).pack(side="left")

        self.charger_liste_accidents()

    def charger_liste_accidents(self):
        for item in self.tree_accidents.get_children():
            self.tree_accidents.delete(item)

        self.accidents_cache.clear()
        session = get_session()
        try:
            accidents = session.query(Accident).order_by(Accident.date.desc()).all()
            for acc in accidents:
                vehicules_str_list = []
                degat_val = ""
                resp_val = ""
                valeur_val = ""

                if acc.vehicules:
                    for av in acc.vehicules:
                        v = av.vehicule
                        if v:
                            vehicules_str_list.append(
                                f"{getattr(v, 'immatriculation', '')} ({getattr(v, 'marque', '')} {getattr(v, 'modele', '')})"
                            )
                        else:
                            vehicules_str_list.append(f"ID {av.vehicule_id}")

                        degat_val = av.degat
                        resp_val = "Oui" if av.responsabilite else "Non"
                        valeur_val = f"{av.valeur:,}" if av.valeur is not None else "0"

                vehicule_info = (
                    ", ".join(vehicules_str_list) if vehicules_str_list else "Aucun"
                )

                photos_list = []
                if acc.photo_path:
                    try:
                        photos_list = json.loads(acc.photo_path)
                    except Exception:
                        pass

                gravite_val = (
                    acc.gravite.value
                    if isinstance(acc.gravite, GraviteEnum)
                    else str(acc.gravite)
                )

                data_tuple = (
                    acc.id,
                    acc.date.strftime("%Y-%m-%d") if acc.date else "",
                    vehicule_info,
                    acc.lieu,
                    gravite_val,
                    acc.type,
                    degat_val,
                    resp_val,
                    valeur_val,
                    len(photos_list),
                )

                self.tree_accidents.insert(
                    "",
                    "end",
                    iid=acc.id,
                    values=data_tuple,
                )

                self.accidents_cache[acc.id] = {
                    "id": acc.id,
                    "date": data_tuple[1],
                    "vehicule": vehicule_info,
                    "lieu": acc.lieu,
                    "gravite": gravite_val,
                    "type": acc.type,
                    "degat": degat_val,
                    "responsabilite": resp_val,
                    "valeur": valeur_val,
                    "photos": len(photos_list),
                    "raw_photos": photos_list
                }
        except Exception as e:
            messagebox.showerror(
                "Erreur de chargement", f"Impossible de charger la liste :\n{e}"
            )
        finally:
            session.close()

    def afficher_details_accident(self, event=None):
        selected = self.tree_accidents.selection()
        if not selected:
            messagebox.showwarning(
                "Attention", "Veuillez sélectionner un accident dans la liste."
            )
            return

        accident_id = int(selected[0])
        accident_info = self.accidents_cache.get(accident_id)

        if accident_info:
            FenetreDetailsAccident(self, accident_info)

    # =========================================================
    # VUE 2 : FORMULAIRE COMPLET D'AJOUT + CARROUSEL
    # =========================================================
    def creer_vue_formulaire(self):
        self.frame_formulaire = tk.Frame(self.content_frame, bg="#F8FAFC")

        form_card = tk.Frame(
            self.frame_formulaire,
            bg="white",
            highlightbackground="#CBD5E1",
            highlightthickness=1,
        )
        form_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        header_form = tk.Label(
            form_card,
            text="📝 Enregistrer un Accident",
            font=("Segoe UI", 14, "bold"),
            fg="#0F172A",
            bg="white",
            anchor="w",
        )
        header_form.pack(fill="x", padx=20, pady=(15, 5))

        tk.Frame(form_card, bg="#CBD5E1", height=1).pack(
            fill="x", padx=20, pady=(0, 15)
        )

        form_grid = tk.Frame(form_card, bg="white")
        form_grid.pack(fill="both", expand=True, padx=20)
        form_grid.columnconfigure(1, weight=1)

        def add_field(label_text, row, is_combo=False, values=None):
            tk.Label(
                form_grid,
                text=label_text,
                font=("Segoe UI", 10, "bold"),
                fg="#475569",
                bg="white",
            ).grid(row=row, column=0, sticky="w", pady=5)
            if is_combo:
                cb = ttk.Combobox(form_grid, values=values, state="readonly")
                cb.grid(row=row, column=1, sticky="ew", pady=5, padx=(10, 0))
                return cb
            else:
                ent = ttk.Entry(form_grid)
                ent.grid(row=row, column=1, sticky="ew", pady=5, padx=(10, 0))
                return ent

        tk.Label(
            form_grid,
            text="Sélectionner le Véhicule",
            font=("Segoe UI", 10, "bold"),
            fg="#475569",
            bg="white",
        ).grid(row=0, column=0, sticky="w", pady=5)
        self.cb_vehicule = ttk.Combobox(form_grid, state="readonly")
        self.cb_vehicule.grid(row=0, column=1, sticky="ew", pady=5, padx=(10, 0))
        self.charger_liste_vehicules()

        self.entry_date = add_field("Date (YYYY-MM-DD)", 1)
        self.entry_date.insert(0, datetime.today().strftime("%Y-%m-%d"))

        self.entry_lieu = add_field("Lieu de l'accident", 2)

        self.cb_gravite = add_field(
            "Gravité", 3, is_combo=True, values=["Mineur", "Majeur"]
        )
        self.cb_gravite.current(0)

        self.cb_type = add_field(
            "Type d'accident", 4, is_combo=True, values=["Matériel", "Physique"]
        )
        self.cb_type.current(0)

        self.cb_degat = add_field(
            "Niveau de Dégât", 5, is_combo=True, values=["Faible", "Moyen", "Élevé"]
        )
        self.cb_degat.current(0)

        self.cb_responsabilite = add_field(
            "Responsable ?", 6, is_combo=True, values=["Oui", "Non"]
        )
        self.cb_responsabilite.current(1)

        self.entry_valeur = add_field("Valeur / Estimation (Ar)", 7)

        btn_frame_photos = tk.Frame(form_grid, bg="white")
        btn_frame_photos.grid(row=8, column=0, columnspan=2, pady=8)

        tk.Button(
            btn_frame_photos,
            text="📷 Ajouter des photos",
            command=self.choisir_photos,
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4,
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame_photos,
            text="🗑️ Vider les photos",
            command=self.vider_photos_selection,
            bg="#64748B",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4,
        ).pack(side="left", padx=5)

        self.listbox_photos = tk.Listbox(
            form_grid,
            height=3,
            font=("Segoe UI", 9),
            bg="#F8FAFC",
            fg="#0F172A",
            bd=1,
            relief="solid",
        )
        self.listbox_photos.grid(
            row=9, column=0, columnspan=2, sticky="ew", pady=(0, 5)
        )
        self.listbox_photos.bind("<<ListboxSelect>>", self.on_select_photo_list)

        tk.Button(
            form_grid,
            text="💾 Enregistrer l'accident",
            command=self.sauvegarder_accident,
            bg="#10B981",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            pady=8,
        ).grid(row=10, column=0, columnspan=2, sticky="ew", pady=(10, 15))

        photo_card = tk.Frame(
            self.frame_formulaire,
            bg="white",
            highlightbackground="#CBD5E1",
            highlightthickness=1,
        )
        photo_card.pack(side="right", fill="both", expand=True, padx=(10, 0))

        header_photo = tk.Label(
            photo_card,
            text="🎬 Aperçu & Carrousel des Photos",
            font=("Segoe UI", 14, "bold"),
            fg="#0F172A",
            bg="white",
            anchor="w",
        )
        header_photo.pack(fill="x", padx=20, pady=(15, 5))

        tk.Frame(photo_card, bg="#CBD5E1", height=1).pack(
            fill="x", padx=20, pady=(0, 15)
        )

        self.image_container = tk.Frame(photo_card, bg="#0F172A", relief="flat")
        self.image_container.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.canvas_photo = tk.Label(
            self.image_container,
            bg="#0F172A",
            fg="#94A3B8",
            text="📸 Aucune photo sélectionnée",
            font=("Segoe UI", 11),
            cursor="hand2"
        )
        self.canvas_photo.pack(fill="both", expand=True)
        self.canvas_photo.bind("<Button-1>", self.agrandir_photo_formulaire)

        ctrl_bar = tk.Frame(photo_card, bg="#1E293B", height=40)
        ctrl_bar.pack(fill="x", padx=15, pady=(0, 10))

        self.btn_prev = tk.Button(
            ctrl_bar,
            text="◀ Précédent",
            bg="#EF4444",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.slide_precedent,
            padx=8,
        )
        self.btn_prev.pack(side="left", padx=10, pady=5)

        self.lbl_counter = tk.Label(
            ctrl_bar,
            text="0 / 0",
            bg="#1E293B",
            fg="white",
            font=("Segoe UI", 10, "bold"),
        )
        self.lbl_counter.pack(side="left", expand=True)

        self.btn_next = tk.Button(
            ctrl_bar,
            text="Suivant ▶",
            bg="#10B981",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.slide_suivant,
            padx=8,
        )
        self.btn_next.pack(side="right", padx=10, pady=5)

        thumb_outer = tk.Frame(photo_card, bg="#F1F5F9", height=80)
        thumb_outer.pack(fill="x", padx=15, pady=(0, 15))

        self.thumb_canvas = tk.Canvas(
            thumb_outer, bg="#F1F5F9", height=70, highlightthickness=0
        )
        self.thumb_scrollbar = ttk.Scrollbar(
            thumb_outer, orient="horizontal", command=self.thumb_canvas.xview
        )
        self.thumb_inner = tk.Frame(self.thumb_canvas, bg="#F1F5F9")

        self.thumb_inner.bind(
            "<Configure>",
            lambda e: self.thumb_canvas.configure(
                scrollregion=self.thumb_canvas.bbox("all")
            ),
        )
        self.thumb_canvas.create_window(
            (0, 0), window=self.thumb_inner, anchor="nw"
        )
        self.thumb_canvas.configure(xscrollcommand=self.thumb_scrollbar.set)

        self.thumb_canvas.pack(fill="x", side="top")
        self.thumb_scrollbar.pack(fill="x", side="bottom")

        self.canvas_photo.bind("<MouseWheel>", self.on_mousewheel)

    def agrandir_photo_formulaire(self, event=None):
        """Permet de voir l'image en plein écran lors de l'édition / enregistrement."""
        if self.photos_selected_paths:
            fp = self.photos_selected_paths[self.current_index]
            try:
                img_pil = Image.open(fp)
                FenetrePleinEcran(self, img_pil)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'agrandir l'image : {e}")

    # =========================================================
    # MÉTHODES DE SAUVEGARDE ET GESTION
    # =========================================================
    def sauvegarder_accident(self):
        session = get_session()
        try:
            selection_vehicule = self.cb_vehicule.get()
            if not selection_vehicule:
                messagebox.showwarning(
                    "Véhicule manquant",
                    "Veuillez sélectionner un véhicule dans la liste.",
                )
                return

            vehicule_id = int(selection_vehicule.split(" — ")[0].strip())

            date_str = self.entry_date.get().strip()
            lieu = self.entry_lieu.get().strip()
            type_acc = self.cb_type.get().strip()
            gravite_str = self.cb_gravite.get().strip()

            if not date_str or not lieu:
                messagebox.showwarning(
                    "Champs incomplets", "Veuillez renseigner la date et le lieu."
                )
                return

            date_acc = datetime.strptime(date_str, "%Y-%m-%d").date()

            try:
                gravite_enum_obj = GraviteEnum(gravite_str)
            except ValueError:
                gravite_enum_obj = GraviteEnum.mineur

            encoded_photos = []
            if self.photos_selected_paths:
                for src_path in self.photos_selected_paths:
                    try:
                        with open(src_path, "rb") as img_file:
                            b64_string = base64.b64encode(img_file.read()).decode("utf-8")
                            encoded_photos.append(b64_string)
                    except Exception as err:
                        print(f"Erreur encodage photo {src_path}: {err}")

            photo_path_json = (
                json.dumps(encoded_photos) if encoded_photos else None
            )

            nouveau_accident = Accident(
                date=date_acc,
                lieu=lieu,
                gravite=gravite_enum_obj,
                type=type_acc,
                photo_path=photo_path_json,
            )
            session.add(nouveau_accident)
            session.flush()

            degat_val = self.cb_degat.get().strip()
            responsabilite_val = self.cb_responsabilite.get() == "Oui"
            valeur_str = self.entry_valeur.get().strip() or "0"
            valeur_int = int(float(valeur_str))

            liaison_vehicule = AccidentVehicule(
                accident_id=nouveau_accident.id,
                vehicule_id=vehicule_id,
                degat=degat_val,
                responsabilite=responsabilite_val,
                valeur=valeur_int,
            )
            session.add(liaison_vehicule)

            session.commit()

            messagebox.showinfo(
                "Succès", "Accident et véhicule associatif enregistrés avec succès !"
            )
            self.vider_champs()
            self.afficher_vue_liste()

        except ValueError as err:
            messagebox.showerror(
                "Erreur de format",
                "Veuillez vérifier les valeurs saisies (Date: YYYY-MM-DD, Valeur:"
                f" Nombre entier).\nDétails : {err}",
            )
        except Exception as e:
            session.rollback()
            messagebox.showerror(
                "Erreur d'enregistrement",
                f"Une erreur est survenue lors de la sauvegarde :\n{e}",
            )
        finally:
            session.close()

    def vider_champs(self):
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.entry_lieu.delete(0, tk.END)
        self.cb_type.current(0)
        self.cb_gravite.current(0)
        self.cb_degat.current(0)
        self.cb_responsabilite.current(1)
        self.entry_valeur.delete(0, tk.END)
        self.vider_photos_selection()

    def afficher_vue_liste(self):
        self.frame_formulaire.pack_forget()
        self.frame_liste.pack(fill="both", expand=True)
        self.btn_action.config(
            text="➕ Ajouter un accident",
            bg="#10B981",
            command=self.basculer_vers_ajout,
        )
        self.charger_liste_accidents()

    def afficher_vue_formulaire(self):
        self.frame_liste.pack_forget()
        self.frame_formulaire.pack(fill="both", expand=True)
        self.btn_action.config(
            text="← Retour à la liste",
            bg="#EF4444",
            command=self.afficher_vue_liste,
        )

    def basculer_vers_ajout(self):
        self.afficher_vue_formulaire()

    def charger_liste_vehicules(self):
        session = get_session()
        try:
            vehicules = session.query(Vehicule).all()
            self.cb_vehicule["values"] = [
                f"{v.id} — {getattr(v, 'immatriculation', '')} ({getattr(v, 'marque', '')} {getattr(v, 'modele', '')})"
                for v in vehicules
            ]
            if self.cb_vehicule["values"]:
                self.cb_vehicule.current(0)
        except Exception as e:
            print(f"Erreur chargement véhicules : {e}")
        finally:
            session.close()

    def choisir_photos(self):
        filepaths = filedialog.askopenfilenames(
            title="Sélectionner des photos de l'accident",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")],
        )
        if filepaths:
            for fp in filepaths:
                if fp not in self.photos_selected_paths:
                    self.photos_selected_paths.append(fp)
                    self.listbox_photos.insert(tk.END, os.path.basename(fp))
            self.current_index = len(self.photos_selected_paths) - 1
            self.actualiser_carrousel()

    def on_select_photo_list(self, event):
        selection = self.listbox_photos.curselection()
        if selection:
            self.current_index = selection[0]
            self.actualiser_carrousel()

    def slide_precedent(self):
        if self.photos_selected_paths:
            self.current_index = (self.current_index - 1) % len(
                self.photos_selected_paths
            )
            self.listbox_photos.selection_clear(0, tk.END)
            self.listbox_photos.selection_set(self.current_index)
            self.actualiser_carrousel()

    def slide_suivant(self):
        if self.photos_selected_paths:
            self.current_index = (self.current_index + 1) % len(
                self.photos_selected_paths
            )
            self.listbox_photos.selection_clear(0, tk.END)
            self.listbox_photos.selection_set(self.current_index)
            self.actualiser_carrousel()

    def on_mousewheel(self, event):
        if event.delta > 0:
            self.slide_precedent()
        else:
            self.slide_suivant()

    def vider_photos_selection(self):
        self.photos_selected_paths.clear()
        self.current_index = 0
        self.listbox_photos.delete(0, tk.END)
        self.canvas_photo.config(
            image="", text="📸 Aucune photo sélectionnée"
        )
        self.lbl_counter.config(text="0 / 0")
        for widget in self.thumb_inner.winfo_children():
            widget.destroy()

    def actualiser_carrousel(self):
        total = len(self.photos_selected_paths)
        if total == 0:
            return

        self.lbl_counter.config(text=f"Photo {self.current_index + 1} / {total}")

        filepath = self.photos_selected_paths[self.current_index]
        try:
            img = Image.open(filepath)
            img.thumbnail((420, 360), Image.Resampling.LANCZOS)
            photo_tk = ImageTk.PhotoImage(img)
            self.tk_images.append(photo_tk)
            self.canvas_photo.config(image=photo_tk, text="")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement image : {e}")

        for widget in self.thumb_inner.winfo_children():
            widget.destroy()

        for i, fp in enumerate(self.photos_selected_paths):
            try:
                thumb_img = Image.open(fp)
                thumb_img = thumb_img.resize((60, 60), Image.Resampling.LANCZOS)
                thumb_tk = ImageTk.PhotoImage(thumb_img)
                self.tk_images.append(thumb_tk)

                border_color = "#EF4444" if i == self.current_index else "#CBD5E1"
                lbl_thumb = tk.Label(
                    self.thumb_inner,
                    image=thumb_tk,
                    bd=3,
                    relief="solid",
                    bg=border_color,
                    cursor="hand2",
                )
                lbl_thumb.pack(side="left", padx=4, pady=4)
                lbl_thumb.bind(
                    "<Button-1>",
                    lambda e, idx=i: self.sauter_a_photo(idx),
                )
            except Exception:
                pass

    def sauter_a_photo(self, idx):
        self.current_index = idx
        self.listbox_photos.selection_clear(0, tk.END)
        self.listbox_photos.selection_set(idx)
        self.actualiser_carrousel()