"""Budgets mensuels (UC6) avec niveau de consommation (UC7)."""
import customtkinter as ctk

from services import budget_service, category_service
from ui import theme
from ui.widgets import (Card, MonthSelector, ask_yes_no, labeled_entry, page_header,
                        primary_button, secondary_button, show_error, show_info)
from utils.dates import month_label, shift_month
from utils.formatters import format_amount, format_percent

LEVEL_TEXT = {"ok": "Dans le budget", "warning": "Attention", "danger": "Dépassé"}


class BudgetsView(ctk.CTkFrame):
    def __init__(self, master, user, app=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        right = page_header(self, "Budgets", "Fixez un plafond de dépense par catégorie")
        self.month_selector = MonthSelector(right, on_change=lambda m: self.refresh())
        self.month_selector.pack()

        form = Card(self)
        form.pack(fill="x", padx=28)
        inner = ctk.CTkFrame(form, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)
        cat_frame = ctk.CTkFrame(inner, fg_color="transparent")
        cat_frame.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(cat_frame, text="Catégorie de dépense", font=theme.SMALL,
                     text_color=theme.MUTED, anchor="w").pack(fill="x")
        self.cat_menu = ctk.CTkOptionMenu(cat_frame, values=[""], width=220,
                                          fg_color=theme.PRIMARY,
                                          button_color=theme.PRIMARY_HOVER)
        self.cat_menu.pack()
        self.amount_entry = labeled_entry(inner, "Budget mensuel (FCFA)", 180, "Ex : 50000")
        self.amount_entry.container.pack(side="left", padx=(0, 10))
        self.amount_entry.bind("<Return>", lambda e: self.save_budget())
        primary_button(inner, "Définir le budget", self.save_budget,
                       width=150).pack(side="left", anchor="s")
        secondary_button(inner, "Reconduire le mois précédent", self.copy_previous,
                         width=220).pack(side="right", anchor="s")

        self.summary = ctk.CTkLabel(self, text="", font=theme.BODY_BOLD, anchor="w")
        self.summary.pack(fill="x", padx=30, pady=(14, 4))
        self.list_card = Card(self)
        self.list_card.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        self.list_box = ctk.CTkScrollableFrame(self.list_card, fg_color="transparent")
        self.list_box.pack(fill="both", expand=True, padx=8, pady=8)

    def refresh(self):
        cats = category_service.list_categories(self.user["id"], "depense")
        self.categories = {c["name"]: c["id"] for c in cats}
        names = list(self.categories) or [""]
        self.cat_menu.configure(values=names)
        if self.cat_menu.get() not in names:
            self.cat_menu.set(names[0])

        month = self.month_selector.get()
        status = budget_service.get_budget_status(self.user["id"], month)
        for w in self.list_box.winfo_children():
            w.destroy()

        if not status:
            self.summary.configure(text=f"Aucun budget défini pour {month_label(month).lower()}.")
            ctk.CTkLabel(self.list_box, text="Utilisez le formulaire ci-dessus pour créer "
                         "votre premier budget, ou reconduisez ceux du mois précédent.",
                         text_color=theme.MUTED).pack(pady=30)
            return

        total_budget = sum(b["budget"] for b in status)
        total_spent = sum(b["spent"] for b in status)
        self.summary.configure(
            text=f"Total budgété : {format_amount(total_budget)}    •    "
                 f"Dépensé : {format_amount(total_spent)}    •    "
                 f"Reste : {format_amount(total_budget - total_spent)}")
        for b in status:
            self._budget_row(b, month)

    def _budget_row(self, b, month):
        color = theme.LEVEL_COLORS[b["level"]]
        row = ctk.CTkFrame(self.list_box, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=8)
        top = ctk.CTkFrame(row, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=b["category"], font=theme.BODY_BOLD).pack(side="left")
        ctk.CTkLabel(top, text=f"  {LEVEL_TEXT[b['level']]}", font=theme.SMALL,
                     text_color=color).pack(side="left")
        ctk.CTkButton(top, text="✕", width=28, height=24, fg_color="transparent",
                      text_color=theme.MUTED, hover_color=theme.BORDER,
                      command=lambda: self.delete_budget(b, month)).pack(side="right")
        ctk.CTkLabel(top, text=f"{format_amount(b['spent'])} / {format_amount(b['budget'])}"
                     f"   ({format_percent(b['ratio'])})", font=theme.BODY
                     ).pack(side="right", padx=8)
        bar = ctk.CTkProgressBar(row, height=12, progress_color=color)
        bar.pack(fill="x", pady=(4, 0))
        bar.set(min(b["ratio"], 1.0))
        remaining = (f"Reste {format_amount(b['remaining'])}" if b["remaining"] >= 0
                     else f"Dépassement de {format_amount(-b['remaining'])}")
        ctk.CTkLabel(row, text=remaining, font=theme.SMALL, text_color=theme.MUTED,
                     anchor="w").pack(fill="x")

    def save_budget(self):
        try:
            category_id = self.categories.get(self.cat_menu.get())
            if category_id is None:
                raise ValueError("Veuillez choisir une catégorie.")
            budget_service.set_budget(self.user["id"], category_id,
                                      self.month_selector.get(), self.amount_entry.get())
        except ValueError as exc:
            show_error(str(exc))
            return
        self.amount_entry.delete(0, "end")
        self.refresh()

    def copy_previous(self):
        month = self.month_selector.get()
        previous = shift_month(month, -1)
        count = budget_service.copy_budgets(self.user["id"], previous, month)
        show_info(f"{count} budget(s) reconduit(s) depuis {month_label(previous).lower()}."
                  if count else f"Aucun nouveau budget à reconduire depuis "
                                f"{month_label(previous).lower()}.")
        self.refresh()

    def delete_budget(self, b, month):
        if ask_yes_no(f"Supprimer le budget « {b['category']} » de "
                      f"{month_label(month).lower()} ?"):
            budget_service.delete_budget(self.user["id"], b["category_id"], month)
            self.refresh()
