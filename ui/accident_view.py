import base64
import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

from database.models.accident import Accident, GraviteEnum
from database.models.accident_vehicule import AccidentVehicule
from database.models.base import get_session
from database.models.vehicule import Vehicule


class Accidents(tk.Frame):

  def __init__(self, parent):
    super().__init__(parent)
    self.configure(bg="#ecf0f1")
    self.photos_selected_paths = []
    self.current_index = 0
    self.tk_images = []

    # =========================================================
    # EN-TÊTE PRINCIPAL
    # =========================================================
    header = tk.Frame(self, bg="#2c3e50", height=60)
    header.pack(fill="x")
    tk.Label(
        header,
        text="SMART AUTORISK — GESTION DES ACCIDENTS",
        bg="#2c3e50",
        fg="#1abc9c",
        font=("Segoe UI", 16, "bold"),
    ).pack(side="left", padx=20, pady=15)

    self.btn_action = tk.Button(
        header,
        text="➕ Ajouter un accident",
        bg="#1abc9c",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=12,
        pady=6,
        command=self.basculer_vers_ajout,
    )
    self.btn_action.pack(side="right", padx=20, pady=12)

    # =========================================================
    # CONTENEUR CENTRAL (Bascule entre Liste et Formulaire)
    # =========================================================
    self.content_frame = ttk.Frame(self)
    self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    self.creer_vue_liste()
    self.creer_vue_formulaire()

    self.afficher_vue_liste()

  # =========================================================
  # VUE 1 : LISTE DES ACCIDENTS (TREEVIEW)
  # =========================================================
  def creer_vue_liste(self):
    self.frame_liste = ttk.Frame(self.content_frame)

    top_bar = ttk.Frame(self.frame_liste)
    top_bar.pack(fill="x", pady=(0, 10))
    ttk.Label(
        top_bar, text="Liste des accidents enregistrés", font=("Segoe UI", 12, "bold")
    ).pack(side="left")
    ttk.Button(
        top_bar, text="🔄 Actualiser", command=self.charger_liste_accidents
    ).pack(side="right")

    columns = ("id", "date", "vehicule", "lieu", "gravite", "type", "photos")
    self.tree_accidents = ttk.Treeview(
        self.frame_liste, columns=columns, show="headings", height=15
    )

    self.tree_accidents.heading("id", text="ID")
    self.tree_accidents.heading("date", text="Date")
    self.tree_accidents.heading("vehicule", text="Véhicule")
    self.tree_accidents.heading("lieu", text="Lieu")
    self.tree_accidents.heading("gravite", text="Gravité")
    self.tree_accidents.heading("type", text="Type")
    self.tree_accidents.heading("photos", text="Nb Photos")

    self.tree_accidents.column("id", width=50, anchor="center")
    self.tree_accidents.column("date", width=100, anchor="center")
    self.tree_accidents.column("vehicule", width=180, anchor="w")
    self.tree_accidents.column("lieu", width=200, anchor="w")
    self.tree_accidents.column("gravite", width=90, anchor="center")
    self.tree_accidents.column("type", width=90, anchor="center")
    self.tree_accidents.column("photos", width=80, anchor="center")

    scrollbar = ttk.Scrollbar(
        self.frame_liste, orient="vertical", command=self.tree_accidents.yview
    )
    self.tree_accidents.configure(yscrollcommand=scrollbar.set)

    self.tree_accidents.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    self.charger_liste_accidents()

  def charger_liste_accidents(self):
    for item in self.tree_accidents.get_children():
      self.tree_accidents.delete(item)

    session = get_session()
    try:
      accidents = session.query(Accident).order_by(Accident.date.desc()).all()
      for acc in accidents:
        vehicules_str_list = []
        if acc.vehicules:
          for av in acc.vehicules:
            v = av.vehicule
            if v:
              vehicules_str_list.append(
                  f"{getattr(v, 'immatriculation', '')} ({getattr(v, 'marque', '')} {getattr(v, 'modele', '')})"
              )
            else:
              vehicules_str_list.append(f"ID {av.vehicule_id}")

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

        self.tree_accidents.insert(
            "",
            "end",
            values=(
                acc.id,
                acc.date.strftime("%Y-%m-%d") if acc.date else "",
                vehicule_info,
                acc.lieu,
                gravite_val,
                acc.type,
                len(photos_list),
            ),
        )
    except Exception as e:
      import traceback

      error_details = traceback.format_exc()
      print(f"Erreur chargement liste : {e}\n{error_details}")
      messagebox.showerror(
          "Erreur de chargement", f"Impossible de charger la liste :\n{e}"
      )
    finally:
      session.close()

  # =========================================================
  # VUE 2 : FORMULAIRE D'AJOUT + CARROUSEL
  # =========================================================
  def creer_vue_formulaire(self):
    self.frame_formulaire = ttk.Frame(self.content_frame)

    form_frame = ttk.LabelFrame(
        self.frame_formulaire, text=" 📝 Enregistrer un Accident "
    )
    form_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    ttk.Label(form_frame, text="Sélectionner le Véhicule").grid(
        row=0, column=0, sticky="w", padx=10, pady=8
    )
    self.cb_vehicule = ttk.Combobox(form_frame, width=28, state="readonly")
    self.cb_vehicule.grid(row=0, column=1, pady=8)
    self.charger_liste_vehicules()

    def add_field(label_text, row, is_combo=False, values=None):
      ttk.Label(form_frame, text=label_text).grid(
          row=row, column=0, sticky="w", padx=10, pady=8
      )
      if is_combo:
        cb = ttk.Combobox(form_frame, values=values, width=28, state="readonly")
        cb.grid(row=row, column=1, pady=8)
        return cb
      else:
        ent = ttk.Entry(form_frame, width=30)
        ent.grid(row=row, column=1, pady=8)
        return ent

    self.entry_date = add_field("Date (YYYY-MM-DD)", 1)
    self.entry_date.insert(0, datetime.today().strftime("%Y-%m-%d"))

    self.entry_lieu = add_field("Lieu", 2)
    self.cb_responsable = add_field(
        "Responsable ?", 3, is_combo=True, values=["Oui", "Non"]
    )
    self.cb_responsable.current(1)

    self.cb_evaluation = add_field(
        "Gravité", 4, is_combo=True, values=["mineur", "majeur"]
    )
    self.cb_evaluation.current(0)

    self.entry_estimation = add_field("Estimation / Valeur (Ar)", 5)

    btn_frame_photos = ttk.Frame(form_frame)
    btn_frame_photos.grid(row=6, column=0, columnspan=2, pady=10)

    ttk.Button(
        btn_frame_photos,
        text="📷 Ajouter des photos",
        command=self.choisir_photos,
    ).pack(side="left", padx=5)
    ttk.Button(
        btn_frame_photos,
        text="🗑️ Vider la liste",
        command=self.vider_photos_selection,
    ).pack(side="left", padx=5)

    self.listbox_photos = tk.Listbox(
        form_frame, height=5, width=35, font=("Segoe UI", 9)
    )
    self.listbox_photos.grid(row=7, column=0, columnspan=2, pady=5)
    self.listbox_photos.bind("<<ListboxSelect>>", self.on_select_photo_list)

    ttk.Button(
        form_frame,
        text="💾 Enregistrer l'accident",
        command=self.sauvegarder_accident,
    ).grid(row=8, column=0, columnspan=2, pady=15)

    photo_frame = ttk.LabelFrame(
        self.frame_formulaire, text=" 🎬 Aperçu & Carrousel des Photos "
    )
    photo_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    self.image_container = tk.Frame(
        photo_frame, bg="#1e272e", relief="sunken", bd=2
    )
    self.image_container.pack(fill="both", expand=True, padx=15, pady=15)

    self.canvas_photo = tk.Label(
        self.image_container,
        bg="#1e272e",
        fg="#bdc3c7",
        text="📸 Aucune photo sélectionnée\nGlissez ou ajoutez des images à gauche",
        font=("Segoe UI", 11),
    )
    self.canvas_photo.pack(fill="both", expand=True)

    ctrl_bar = tk.Frame(photo_frame, bg="#2f3640", height=45)
    ctrl_bar.pack(fill="x", padx=15, pady=(0, 10))

    self.btn_prev = tk.Button(
        ctrl_bar,
        text="◀ Précédent",
        bg="#c23616",
        fg="white",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        cursor="hand2",
        command=self.slide_precedent,
    )
    self.btn_prev.pack(side="left", padx=10, pady=6)

    self.lbl_counter = tk.Label(
        ctrl_bar,
        text="0 / 0",
        bg="#2f3640",
        fg="#f5f6fa",
        font=("Segoe UI", 10, "bold"),
    )
    self.lbl_counter.pack(side="left", expand=True)

    self.btn_next = tk.Button(
        ctrl_bar,
        text="Suivant ▶",
        bg="#44bd32",
        fg="white",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        cursor="hand2",
        command=self.slide_suivant,
    )
    self.btn_next.pack(side="right", padx=10, pady=6)

    thumb_outer = tk.Frame(photo_frame, bg="#f5f6fa", height=85)
    thumb_outer.pack(fill="x", padx=15, pady=(0, 15))

    self.thumb_canvas = tk.Canvas(
        thumb_outer, bg="#f5f6fa", height=75, highlightthickness=0
    )
    self.thumb_scrollbar = ttk.Scrollbar(
        thumb_outer, orient="horizontal", command=self.thumb_canvas.xview
    )
    self.thumb_inner = tk.Frame(self.thumb_canvas, bg="#f5f6fa")

    self.thumb_inner.bind(
        "<Configure>",
        lambda e: self.thumb_canvas.configure(
            scrollregion=self.thumb_canvas.bbox("all")
        ),
    )
    self.thumb_canvas.create_window((0, 0), window=self.thumb_inner, anchor="nw")
    self.thumb_canvas.configure(xscrollcommand=self.thumb_scrollbar.set)

    self.thumb_canvas.pack(fill="x", side="top")
    self.thumb_scrollbar.pack(fill="x", side="bottom")

    self.canvas_photo.bind("<MouseWheel>", self.on_mousewheel)

  # =========================================================
  # MÉTHODES DE NAVIGATION ET GESTION
  # =========================================================
  def afficher_vue_liste(self):
    self.frame_formulaire.pack_forget()
    self.frame_liste.pack(fill="both", expand=True)
    self.btn_action.config(
        text="➕ Ajouter un accident",
        bg="#1abc9c",
        command=self.basculer_vers_ajout,
    )
    self.charger_liste_accidents()

  def afficher_vue_formulaire(self):
    self.frame_liste.pack_forget()
    self.frame_formulaire.pack(fill="both", expand=True)
    self.btn_action.config(
        text="← Retour à la liste",
        bg="#e74c3c",
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
        image="",
        text="📸 Aucune photo sélectionnée\nGlissez ou ajoutez des images à gauche",
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

        border_color = "#e74c3c" if i == self.current_index else "#bdc3c7"
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

  def sauvegarder_accident(self):
    session = get_session()
    try:
      selection_vehicule = self.cb_vehicule.get()
      if not selection_vehicule:
        messagebox.showwarning(
            "Véhicule manquant", "Veuillez sélectionner un véhicule dans la liste."
        )
        return

      vehicule_id_str = selection_vehicule.split(" — ")[0].strip()
      vehicule_id = int(vehicule_id_str)

      date_str = self.entry_date.get().strip()
      lieu = self.entry_lieu.get().strip()
      responsable_str = self.cb_responsable.get()
      val_gravite_str = self.cb_evaluation.get().strip().lower()

      try:
        gravite_enum_obj = GraviteEnum(val_gravite_str)
      except ValueError:
        gravite_enum_obj = GraviteEnum.mineur

      estimation_str = self.entry_estimation.get().strip() or "0"

      if not date_str or not lieu:
        messagebox.showwarning(
            "Champs incomplets", "Veuillez renseigner la date et le lieu."
        )
        return

      date_acc = datetime.strptime(date_str, "%Y-%m-%d").date()

      encoded_photos = []
      if self.photos_selected_paths:
        for src_path in self.photos_selected_paths:
          try:
            with open(src_path, "rb") as img_file:
              b64_string = base64.b64encode(img_file.read()).decode("utf-8")
              encoded_photos.append(b64_string)
          except Exception as err:
            print(f"Erreur d'encodage de {src_path}: %s" % err)

      nouveau_accident = Accident(
          date=date_acc,
          lieu=lieu,
          gravite=gravite_enum_obj,
          type="matériel",
          photo_path=json.dumps(encoded_photos) if encoded_photos else None,
      )
      session.add(nouveau_accident)
      session.flush()

      liaison_vehicule = AccidentVehicule(
          accident_id=nouveau_accident.id,
          vehicule_id=vehicule_id,
          degat=gravite_enum_obj,
          responsabilite=(responsable_str == "Oui"),
          role="fautif",
          valeur=int(float(estimation_str)),
      )
      session.add(liaison_vehicule)
      session.commit()

      messagebox.showinfo(
          "Succès",
          f"Accident enregistré avec {len(encoded_photos)} photo(s) encodées en Base64 !",
      )
      self.vider_champs()
      self.afficher_vue_liste()

    except ValueError as err:
      messagebox.showerror(
          "Erreur format",
          f"Vérifiez le format des champs (date YYYY-MM-DD / nombre) : {err}",
      )
    except Exception as e:
      session.rollback()
      messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {e}")
    finally:
      session.close()

  def vider_champs(self):
    self.entry_date.delete(0, tk.END)
    self.entry_date.insert(0, datetime.today().strftime("%Y-%m-%d"))
    self.entry_lieu.delete(0, tk.END)
    self.cb_evaluation.current(0)
    self.entry_estimation.delete(0, tk.END)
    self.vider_photos_selection()