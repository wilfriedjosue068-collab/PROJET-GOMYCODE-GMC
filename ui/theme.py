"""Couleurs, polices et style des tableaux (thème clair / sombre)."""
from tkinter import ttk

import customtkinter as ctk

PRIMARY = "#0E7C66"
PRIMARY_HOVER = "#0A5E4E"
INCOME = "#16A34A"
EXPENSE = "#DC2626"
WARNING = "#D97706"
INFO = "#2563EB"

# (couleur thème clair, couleur thème sombre)
BG = ("#F3F5F7", "#16181B")
CARD = ("#FFFFFF", "#23262B")
SIDEBAR = ("#0F2A26", "#0B1F1C")
BORDER = ("#E3E7EB", "#33373D")
TEXT = ("#1F2937", "#E5E7EB")
MUTED = ("#6B7280", "#9CA3AF")

LEVEL_COLORS = {"ok": INCOME, "warning": WARNING, "danger": EXPENSE}

CHART_PALETTE = ["#0E7C66", "#2563EB", "#D97706", "#DC2626", "#7C3AED",
                 "#0891B2", "#DB2777", "#65A30D", "#9CA3AF"]

FONT = "Segoe UI"
TITLE = (FONT, 22, "bold")
SUBTITLE = (FONT, 15, "bold")
BODY = (FONT, 13)
BODY_BOLD = (FONT, 13, "bold")
SMALL = (FONT, 11)
BIG_NUMBER = (FONT, 20, "bold")


def is_dark():
    return ctk.get_appearance_mode() == "Dark"


def pick(pair):
    """Retourne la couleur adaptée au thème courant à partir d'un tuple (clair, sombre)."""
    return pair[1] if is_dark() else pair[0]


def apply_treeview_style():
    """Harmonise les tableaux ttk.Treeview avec le thème CustomTkinter."""
    style = ttk.Style()
    style.theme_use("default")
    bg, fg, head = pick(CARD), pick(TEXT), pick(BG)
    style.configure("Treeview", background=bg, fieldbackground=bg, foreground=fg,
                    rowheight=28, font=(FONT, 10), borderwidth=0)
    style.configure("Treeview.Heading", background=head, foreground=fg,
                    font=(FONT, 10, "bold"), relief="flat", padding=6)
    style.map("Treeview", background=[("selected", PRIMARY)],
              foreground=[("selected", "#FFFFFF")])
    style.map("Treeview.Heading", background=[("active", head)])
