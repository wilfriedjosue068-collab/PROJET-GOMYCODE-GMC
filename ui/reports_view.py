"""Rapports (bilan sur 12 mois) et export des transactions (UC9)."""
from tkinter import filedialog

import customtkinter as ctk

from services import export_service, report_service
from ui import theme
from ui.widgets import (Card, DataTable, labeled_entry, page_header, primary_button,
                        secondary_button, show_error, show_info)
from utils.dates import current_month, month_label
from utils.formatters import format_amount


class ReportsView(ctk.CTkFrame):
    def __init__(self, master, user, app=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        page_header(self, "Rapports & export", "Bilan annuel et export de vos données")

        export = Card(self)
        export.pack(fill="x", padx=28)
        ctk.CTkLabel(export, text="Exporter les transactions", font=theme.SUBTITLE,
                     anchor="w").pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(export, text="Laissez les dates vides pour tout exporter.",
                     font=theme.SMALL, text_color=theme.MUTED,
                     anchor="w").pack(fill="x", padx=16)
        inner = ctk.CTkFrame(export, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)
        self.start_entry = labeled_entry(inner, "Du", 130, "JJ/MM/AAAA")
        self.start_entry.container.pack(side="left", padx=(0, 10))
        self.end_entry = labeled_entry(inner, "Au", 130, "JJ/MM/AAAA")
        self.end_entry.container.pack(side="left", padx=(0, 16))
        primary_button(inner, "Exporter en Excel", lambda: self.export("xlsx"),
                       width=160).pack(side="left", anchor="s")
        secondary_button(inner, "Exporter en CSV", lambda: self.export("csv"),
                         width=150).pack(side="left", anchor="s", padx=8)

        table_card = Card(self)
        table_card.pack(fill="both", expand=True, padx=28, pady=14)
        ctk.CTkLabel(table_card, text="Bilan des 12 derniers mois", font=theme.SUBTITLE,
                     anchor="w").pack(fill="x", padx=16, pady=(12, 0))
        self.table = DataTable(table_card, [
            ("month", "Mois", 180, "w"),
            ("revenus", "Revenus", 170, "e"),
            ("depenses", "Dépenses", 170, "e"),
            ("solde", "Solde", 170, "e"),
            ("taux", "Taux d'épargne", 140, "e"),
        ], height=12)
        self.table.pack(fill="both", expand=True, padx=12, pady=12)
        self.table.tree.tag_configure("negatif", foreground=theme.EXPENSE)
        self.total_label = ctk.CTkLabel(self, text="", font=theme.BODY_BOLD, anchor="w")
        self.total_label.pack(fill="x", padx=30, pady=(0, 24))

    def refresh(self):
        trend = [t for t in report_service.get_monthly_trend(self.user["id"], current_month(), 12)
                 if t["nb_transactions"]]
        self.table.clear()
        for i, t in enumerate(reversed(trend)):
            rate = f"{t['solde'] / t['revenus']:.0%}" if t["revenus"] else "-"
            self.table.insert(i, (month_label(t["month"]), format_amount(t["revenus"]),
                                  format_amount(t["depenses"]),
                                  format_amount(t["solde"], signed=True), rate),
                              tag="negatif" if t["solde"] < 0 else None)
        income = sum(t["revenus"] for t in trend)
        expense = sum(t["depenses"] for t in trend)
        self.total_label.configure(
            text=f"Sur 12 mois : revenus {format_amount(income)}  •  dépenses "
                 f"{format_amount(expense)}  •  épargne {format_amount(income - expense, signed=True)}")

    def export(self, fmt):
        ext = ".xlsx" if fmt == "xlsx" else ".csv"
        path = filedialog.asksaveasfilename(
            defaultextension=ext, initialfile=f"moneytrack_transactions{ext}",
            filetypes=[("Excel", "*.xlsx")] if fmt == "xlsx" else [("CSV", "*.csv")])
        if not path:
            return
        func = export_service.export_excel if fmt == "xlsx" else export_service.export_csv
        try:
            count = func(self.user["id"], path, start=self.start_entry.get().strip() or None,
                         end=self.end_entry.get().strip() or None)
        except (ValueError, OSError) as exc:
            show_error(f"Export impossible : {exc}")
            return
        show_info(f"{count} transaction(s) exportée(s) vers :\n{path}")
