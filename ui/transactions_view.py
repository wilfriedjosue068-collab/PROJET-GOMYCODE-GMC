"""Gestion des transactions : saisie (UC3), modification/suppression (UC4), historique (UC5)."""
import customtkinter as ctk

from services import category_service, transaction_service
from ui import theme
from ui.widgets import (Card, DataTable, ask_yes_no, labeled_entry, page_header,
                        primary_button, secondary_button, show_error)
from utils.dates import today_ui
from utils.formatters import format_amount, format_date, type_label

TYPE_FILTERS = {"Tous": None, "Revenus": "revenu", "Dépenses": "depense"}
ALL_CATEGORIES = "Toutes"


class TransactionsView(ctk.CTkFrame):
    def __init__(self, master, user, app=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.categories = {}

        right = page_header(self, "Transactions", "Historique de vos revenus et dépenses")
        primary_button(right, "+  Nouvelle transaction", self.open_add_dialog,
                       width=200).pack()

        # --- Filtres ---
        filters = Card(self)
        filters.pack(fill="x", padx=28)
        inner = ctk.CTkFrame(filters, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        self.type_filter = self._option(inner, "Type", list(TYPE_FILTERS), 110,
                                        lambda _: self._on_type_filter())
        self.cat_filter = self._option(inner, "Catégorie", [ALL_CATEGORIES], 170,
                                       lambda _: self.refresh())
        self.start_entry = labeled_entry(inner, "Du", 110, "JJ/MM/AAAA")
        self.start_entry.container.pack(side="left", padx=(0, 10))
        self.end_entry = labeled_entry(inner, "Au", 110, "JJ/MM/AAAA")
        self.end_entry.container.pack(side="left", padx=(0, 10))
        self.search_entry = labeled_entry(inner, "Recherche", 180, "Description…")
        self.search_entry.container.pack(side="left", padx=(0, 10))
        for entry in (self.start_entry, self.end_entry, self.search_entry):
            entry.bind("<Return>", lambda e: self.refresh())

        buttons = ctk.CTkFrame(inner, fg_color="transparent")
        buttons.pack(side="left", anchor="s")
        primary_button(buttons, "Filtrer", self.refresh, width=90).pack(side="left")
        secondary_button(buttons, "Réinitialiser", self.reset_filters,
                         width=110).pack(side="left", padx=6)

        # --- Tableau ---
        table_card = Card(self)
        table_card.pack(fill="both", expand=True, padx=28, pady=14)
        self.table = DataTable(table_card, [
            ("date", "Date", 100, "center"),
            ("type", "Type", 90, "center"),
            ("category", "Catégorie", 170, "w"),
            ("description", "Description", 300, "w"),
            ("amount", "Montant", 150, "e"),
        ], height=14)
        self.table.pack(fill="both", expand=True, padx=12, pady=12)
        self.table.tree.bind("<Double-1>", lambda e: self.open_edit_dialog())

        # --- Pied : totaux + actions ---
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=28, pady=(0, 24))
        self.totals_label = ctk.CTkLabel(footer, text="", font=theme.BODY, anchor="w")
        self.totals_label.pack(side="left")
        secondary_button(footer, "Supprimer", self.delete_selected).pack(side="right")
        secondary_button(footer, "Modifier", self.open_edit_dialog).pack(side="right", padx=8)

    def _option(self, parent, label, values, width, command):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(frame, text=label, font=theme.SMALL, text_color=theme.MUTED,
                     anchor="w").pack(fill="x")
        menu = ctk.CTkOptionMenu(frame, values=values, width=width, command=command,
                                 fg_color=theme.PRIMARY, button_color=theme.PRIMARY_HOVER)
        menu.pack()
        return menu

    # ------------------------------------------------------------------
    def _load_categories(self):
        type_ = TYPE_FILTERS[self.type_filter.get()]
        cats = category_service.list_categories(self.user["id"], type_)
        self.categories = {c["name"]: c["id"] for c in cats}
        values = [ALL_CATEGORIES] + list(self.categories)
        self.cat_filter.configure(values=values)
        if self.cat_filter.get() not in values:
            self.cat_filter.set(ALL_CATEGORIES)

    def _on_type_filter(self):
        self.cat_filter.set(ALL_CATEGORIES)
        self.refresh()

    def reset_filters(self):
        self.type_filter.set("Tous")
        self.cat_filter.set(ALL_CATEGORIES)
        for entry in (self.start_entry, self.end_entry, self.search_entry):
            entry.delete(0, "end")
        self.focus_set()
        self.refresh()

    def refresh(self):
        self._load_categories()
        try:
            transactions = transaction_service.list_transactions(
                self.user["id"],
                start=self.start_entry.get().strip() or None,
                end=self.end_entry.get().strip() or None,
                category_id=self.categories.get(self.cat_filter.get()),
                type_=TYPE_FILTERS[self.type_filter.get()],
                search=self.search_entry.get(),
            )
        except ValueError as exc:
            show_error(str(exc))
            return
        self.table.clear()
        for t in transactions:
            sign = 1 if t["type"] == "revenu" else -1
            self.table.insert(t["id"], (
                format_date(t["date"]), type_label(t["type"]), t["category"],
                t["description"], format_amount(sign * t["amount"], signed=True),
            ), tag=t["type"])
        totals = transaction_service.compute_totals(transactions)
        self.totals_label.configure(
            text=f"{len(transactions)} transaction(s)   |   Revenus : "
                 f"{format_amount(totals['revenus'])}   |   Dépenses : "
                 f"{format_amount(totals['depenses'])}   |   Solde : "
                 f"{format_amount(totals['solde'], signed=True)}")

    # ------------------------------------------------------------------
    def open_add_dialog(self):
        TransactionDialog(self, self.user, on_saved=self.refresh)

    def open_edit_dialog(self):
        tid = self.table.selected_id()
        if tid is None:
            show_error("Sélectionnez d'abord une transaction dans le tableau.")
            return
        transaction = transaction_service.get_transaction(tid, self.user["id"])
        TransactionDialog(self, self.user, on_saved=self.refresh, transaction=transaction)

    def delete_selected(self):
        tid = self.table.selected_id()
        if tid is None:
            show_error("Sélectionnez d'abord une transaction dans le tableau.")
            return
        if ask_yes_no("Supprimer définitivement cette transaction ?"):
            transaction_service.delete_transaction(tid, self.user["id"])
            self.refresh()


class TransactionDialog(ctk.CTkToplevel):
    """Fenêtre de saisie ou de modification d'une transaction."""

    def __init__(self, master, user, on_saved, transaction=None):
        super().__init__(master)
        self.user = user
        self.on_saved = on_saved
        self.transaction = transaction
        self.title("Modifier la transaction" if transaction else "Nouvelle transaction")
        top = master.winfo_toplevel()
        x = top.winfo_rootx() + (top.winfo_width() - 420) // 2
        y = top.winfo_rooty() + (top.winfo_height() - 470) // 2
        self.geometry(f"420x470+{max(x, 0)}+{max(y, 0)}")
        self.resizable(False, False)
        self.configure(fg_color=theme.CARD)
        self.transient(master.winfo_toplevel())

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=20)

        ctk.CTkLabel(body, text=self.title(), font=theme.SUBTITLE).pack(anchor="w", pady=(0, 12))
        self.type_switch = ctk.CTkSegmentedButton(
            body, values=["Dépense", "Revenu"], command=lambda _: self._load_categories(),
            selected_color=theme.PRIMARY, selected_hover_color=theme.PRIMARY_HOVER)
        self.type_switch.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(body, text="Catégorie", font=theme.SMALL, text_color=theme.MUTED,
                     anchor="w").pack(fill="x")
        self.category_menu = ctk.CTkOptionMenu(body, values=[""], fg_color=theme.PRIMARY,
                                               button_color=theme.PRIMARY_HOVER)
        self.category_menu.pack(fill="x", pady=(0, 10))

        self.amount_entry = labeled_entry(body, "Montant (FCFA)", placeholder="Ex : 12500")
        self.amount_entry.container.pack(fill="x", pady=(0, 10))
        self.date_entry = labeled_entry(body, "Date", placeholder="JJ/MM/AAAA")
        self.date_entry.container.pack(fill="x", pady=(0, 10))
        self.desc_entry = labeled_entry(body, "Description (facultatif)")
        self.desc_entry.container.pack(fill="x", pady=(0, 16))

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x")
        primary_button(buttons, "Enregistrer", self.save, width=170).pack(side="right")
        secondary_button(buttons, "Annuler", self.destroy).pack(side="right", padx=8)

        if transaction:
            self.type_switch.set("Revenu" if transaction["type"] == "revenu" else "Dépense")
            self._load_categories()
            self.category_menu.set(transaction["category"])
            self.amount_entry.insert(0, str(transaction["amount"]))
            self.date_entry.insert(0, format_date(transaction["date"]))
            self.desc_entry.insert(0, transaction["description"])
        else:
            self.type_switch.set("Dépense")
            self._load_categories()
            self.date_entry.insert(0, today_ui())

        self.bind("<Return>", lambda e: self.save())
        self.bind("<Escape>", lambda e: self.destroy())
        self.after(150, self._make_modal)

    def _make_modal(self):
        try:
            self.grab_set()
            self.amount_entry.focus_set()
        except Exception:  # la fenêtre a pu être fermée entre-temps
            pass

    def _load_categories(self):
        type_ = "revenu" if self.type_switch.get() == "Revenu" else "depense"
        cats = category_service.list_categories(self.user["id"], type_)
        self.categories = {c["name"]: c["id"] for c in cats}
        names = list(self.categories) or ["(aucune catégorie)"]
        self.category_menu.configure(values=names)
        self.category_menu.set(names[0])

    def save(self):
        category_id = self.categories.get(self.category_menu.get())
        try:
            if category_id is None:
                raise ValueError("Veuillez d'abord créer une catégorie.")
            args = (self.user["id"], category_id, self.amount_entry.get(),
                    self.date_entry.get(), self.desc_entry.get())
            if self.transaction:
                transaction_service.update_transaction(self.transaction["id"], *args)
            else:
                transaction_service.add_transaction(*args)
        except ValueError as exc:
            show_error(str(exc), parent=self)
            return
        self.destroy()
        self.on_saved()
