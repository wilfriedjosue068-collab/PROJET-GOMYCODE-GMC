"""Composants graphiques réutilisables."""
from tkinter import messagebox, ttk

import customtkinter as ctk

from ui import theme
from utils.dates import current_month, month_label, shift_month


class Card(ctk.CTkFrame):
    """Cadre blanc arrondi servant de conteneur."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", theme.CARD)
        kwargs.setdefault("corner_radius", 12)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", theme.BORDER)
        super().__init__(master, **kwargs)


class StatCard(Card):
    """Carte d'indicateur : titre + grande valeur colorée."""

    def __init__(self, master, title, color=None):
        super().__init__(master)
        ctk.CTkLabel(self, text=title, font=theme.BODY, text_color=theme.MUTED,
                     anchor="w").pack(fill="x", padx=16, pady=(14, 0))
        self.value = ctk.CTkLabel(self, text="-", font=theme.BIG_NUMBER,
                                  text_color=color or theme.TEXT, anchor="w")
        self.value.pack(fill="x", padx=16, pady=(2, 14))

    def set(self, text, color=None):
        self.value.configure(text=text)
        if color:
            self.value.configure(text_color=color)


class MonthSelector(ctk.CTkFrame):
    """Sélecteur ◀ Septembre 2026 ▶ ; appelle on_change(mois) à chaque changement."""

    def __init__(self, master, on_change, month=None):
        super().__init__(master, fg_color="transparent")
        self.month = month or current_month()
        self.on_change = on_change
        ctk.CTkButton(self, text="◀", width=34, command=lambda: self._shift(-1),
                      fg_color=theme.CARD, text_color=theme.TEXT,
                      hover_color=theme.BORDER).pack(side="left")
        self.label = ctk.CTkLabel(self, text="", font=theme.BODY_BOLD, width=150)
        self.label.pack(side="left", padx=6)
        ctk.CTkButton(self, text="▶", width=34, command=lambda: self._shift(1),
                      fg_color=theme.CARD, text_color=theme.TEXT,
                      hover_color=theme.BORDER).pack(side="left")
        self._update_label()

    def _shift(self, delta):
        self.month = shift_month(self.month, delta)
        self._update_label()
        self.on_change(self.month)

    def _update_label(self):
        self.label.configure(text=month_label(self.month))

    def get(self):
        return self.month


class DataTable(ctk.CTkFrame):
    """Tableau (ttk.Treeview) avec barre de défilement."""

    def __init__(self, master, columns, height=12):
        super().__init__(master, fg_color="transparent")
        self.tree = ttk.Treeview(self, columns=[c[0] for c in columns],
                                 show="headings", height=height, selectmode="browse")
        for key, label, width, anchor in columns:
            self.tree.heading(key, text=label, anchor=anchor)
            self.tree.column(key, width=width, anchor=anchor, stretch=(anchor == "w"))
        scrollbar = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.tag_configure("revenu", foreground=theme.INCOME)
        self.tree.tag_configure("depense", foreground=theme.EXPENSE)

    def clear(self):
        self.tree.delete(*self.tree.get_children())

    def insert(self, iid, values, tag=None):
        self.tree.insert("", "end", iid=str(iid), values=values, tags=(tag,) if tag else ())

    def selected_id(self):
        selection = self.tree.selection()
        return int(selection[0]) if selection else None


def labeled_entry(master, label, width=200, placeholder="", show=None):
    """Crée un libellé + champ de saisie empilés ; retourne le champ."""
    frame = ctk.CTkFrame(master, fg_color="transparent")
    ctk.CTkLabel(frame, text=label, font=theme.SMALL, text_color=theme.MUTED,
                 anchor="w").pack(fill="x")
    entry = ctk.CTkEntry(frame, width=width, placeholder_text=placeholder, show=show)
    entry.pack(fill="x")
    entry.container = frame
    return entry


def show_error(message, parent=None):
    messagebox.showerror("MoneyTrack", message, parent=parent)


def show_info(message, parent=None):
    messagebox.showinfo("MoneyTrack", message, parent=parent)


def ask_yes_no(message, parent=None):
    return messagebox.askyesno("MoneyTrack", message, parent=parent)


def primary_button(master, text, command, width=160, **kwargs):
    return ctk.CTkButton(master, text=text, command=command, width=width, height=34,
                         fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_HOVER,
                         font=theme.BODY_BOLD, **kwargs)


def secondary_button(master, text, command, width=120, **kwargs):
    return ctk.CTkButton(master, text=text, command=command, width=width, height=34,
                         fg_color="transparent", border_width=1,
                         border_color=theme.BORDER, text_color=theme.TEXT,
                         hover_color=theme.BORDER, font=theme.BODY, **kwargs)


def page_header(master, title, subtitle=None):
    """En-tête de page ; retourne le cadre de droite pour y placer des boutons."""
    header = ctk.CTkFrame(master, fg_color="transparent")
    header.pack(fill="x", padx=28, pady=(24, 12))
    left = ctk.CTkFrame(header, fg_color="transparent")
    left.pack(side="left")
    ctk.CTkLabel(left, text=title, font=theme.TITLE, anchor="w").pack(anchor="w")
    if subtitle:
        ctk.CTkLabel(left, text=subtitle, font=theme.BODY, text_color=theme.MUTED,
                     anchor="w").pack(anchor="w")
    right = ctk.CTkFrame(header, fg_color="transparent", width=1, height=1)
    right.pack(side="right")
    return right
