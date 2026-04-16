import tkinter as tk
from tkinter import ttk

class Dashboard(tk.Frame):

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
            text="SMART AUTORISK - DASHBOARD",
            bg="#2c3e50",
            fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=15)