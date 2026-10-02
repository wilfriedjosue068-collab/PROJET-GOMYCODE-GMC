"""Gestion des catégories (UC2)."""
import customtkinter as ctk

from services import category_service
from ui import theme
from ui.widgets import (Card, ask_yes_no, labeled_entry, page_header, primary_button,
                        show_error)

TYPES = {"Dépense": "depense", "Revenu": "revenu"}


class CategoriesView(ctk.CTkFrame):
    def __init__(self, master, user, app=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        page_header(self, "Catégories", "Organisez vos revenus et dépenses")

        form = Card(self)
        form.pack(fill="x", padx=28)
        inner = ctk.CTkFrame(form, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)
        self.name_entry = labeled_entry(inner, "Nouvelle catégorie", 260, "Ex : Tontine")
        self.name_entry.container.pack(side="left", padx=(0, 10))
        self.name_entry.bind("<Return>", lambda e: self.add())
        type_frame = ctk.CTkFrame(inner, fg_color="transparent")
        type_frame.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(type_frame, text="Type", font=theme.SMALL, text_color=theme.MUTED,
                     anchor="w").pack(fill="x")
        self.type_switch = ctk.CTkSegmentedButton(
            type_frame, values=list(TYPES), selected_color=theme.PRIMARY,
            selected_hover_color=theme.PRIMARY_HOVER)
        self.type_switch.set("Dépense")
        self.type_switch.pack()
        primary_button(inner, "Ajouter", self.add, width=110).pack(side="left", anchor="s")

        columns = ctk.CTkFrame(self, fg_color="transparent")
        columns.pack(fill="both", expand=True, padx=28, pady=14)
        columns.grid_columnconfigure((0, 1), weight=1, uniform="cols")
        columns.grid_rowconfigure(0, weight=1)
        self.lists = {}
        for col, (title, type_, color) in enumerate((
                ("Catégories de dépenses", "depense", theme.EXPENSE),
                ("Catégories de revenus", "revenu", theme.INCOME))):
            card = Card(columns)
            card.grid(row=0, column=col, sticky="nsew", padx=(0, 12) if col == 0 else 0)
            ctk.CTkLabel(card, text=title, font=theme.SUBTITLE, text_color=color,
                         anchor="w").pack(fill="x", padx=16, pady=(12, 4))
            box = ctk.CTkScrollableFrame(card, fg_color="transparent")
            box.pack(fill="both", expand=True, padx=8, pady=(0, 12))
            self.lists[type_] = box

    def refresh(self):
        for type_, box in self.lists.items():
            for w in box.winfo_children():
                w.destroy()
            for cat in category_service.list_categories(self.user["id"], type_):
                row = ctk.CTkFrame(box, fg_color="transparent")
                row.pack(fill="x", pady=2, padx=4)
                ctk.CTkLabel(row, text=cat["name"], font=theme.BODY,
                             anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkButton(row, text="Supprimer", width=84, height=28,
                              fg_color="transparent", text_color=theme.EXPENSE,
                              hover_color=theme.BORDER,
                              command=lambda c=cat: self.delete(c)).pack(side="right")
                ctk.CTkButton(row, text="Renommer", width=84, height=28,
                              fg_color="transparent", text_color=theme.TEXT,
                              hover_color=theme.BORDER,
                              command=lambda c=cat: self.rename(c)).pack(side="right")

    def add(self):
        try:
            category_service.add_category(self.user["id"], self.name_entry.get(),
                                          TYPES[self.type_switch.get()])
        except ValueError as exc:
            show_error(str(exc))
            return
        self.name_entry.delete(0, "end")
        self.refresh()

    def rename(self, cat):
        dialog = ctk.CTkInputDialog(title="Renommer",
                                    text=f"Nouveau nom pour « {cat['name']} » :")
        new_name = dialog.get_input()
        if not new_name:
            return
        try:
            category_service.rename_category(cat["id"], self.user["id"], new_name)
        except ValueError as exc:
            show_error(str(exc))
            return
        self.refresh()

    def delete(self, cat):
        if not ask_yes_no(f"Supprimer la catégorie « {cat['name']} » ?"):
            return
        try:
            category_service.delete_category(cat["id"], self.user["id"])
        except ValueError as exc:
            show_error(str(exc))
            return
        self.refresh()
