"""Fenêtre principale : écran de connexion puis interface avec menu latéral."""
import customtkinter as ctk

import config
from ui import theme
from ui.budgets_view import BudgetsView
from ui.categories_view import CategoriesView
from ui.dashboard_view import DashboardView
from ui.login_view import LoginView
from ui.reports_view import ReportsView
from ui.settings_view import SettingsView
from ui.transactions_view import TransactionsView

PAGES = [
    ("dashboard", "Tableau de bord", "▣", DashboardView),
    ("transactions", "Transactions", "⇄", TransactionsView),
    ("categories", "Catégories", "▦", CategoriesView),
    ("budgets", "Budgets", "◔", BudgetsView),
    ("reports", "Rapports & export", "▤", ReportsView),
    ("settings", "Paramètres", "⚙", SettingsView),
]


class MoneyTrackApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{config.APP_NAME} - Gestion budgétaire personnelle")
        self.geometry("1240x780")
        self.minsize(1080, 680)
        self.configure(fg_color=theme.BG)
        theme.apply_treeview_style()
        self.user = None
        self.current_screen = None
        self.show_login()

    def _set_screen(self, widget):
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = widget
        widget.pack(fill="both", expand=True)

    def show_login(self):
        self.user = None
        self._set_screen(LoginView(self, on_success=self.on_login))

    def on_login(self, user):
        self.user = user
        self._set_screen(MainView(self, user, on_logout=self.show_login))


class MainView(ctk.CTkFrame):
    """Menu latéral + zone de contenu. Les pages sont créées à la première visite."""

    def __init__(self, master, user, on_logout):
        super().__init__(master, fg_color=theme.BG, corner_radius=0)
        self.user = user
        self.on_logout = on_logout
        self.pages = {}
        self.buttons = {}
        self.active = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self.content = ctk.CTkFrame(self, fg_color=theme.BG, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.show_page("dashboard")

    def _build_sidebar(self):
        bar = ctk.CTkFrame(self, width=230, fg_color=theme.SIDEBAR, corner_radius=0)
        bar.grid(row=0, column=0, sticky="nsw")
        bar.grid_propagate(False)
        bar.pack_propagate(False)

        ctk.CTkLabel(bar, text="MoneyTrack", font=(theme.FONT, 24, "bold"),
                     text_color="#FFFFFF").pack(anchor="w", padx=24, pady=(28, 0))
        ctk.CTkLabel(bar, text="Budget personnel", font=theme.SMALL,
                     text_color="#8FB8AE").pack(anchor="w", padx=24, pady=(0, 24))

        for key, label, icon, _ in PAGES:
            btn = ctk.CTkButton(bar, text=f"  {icon}   {label}", anchor="w", height=40,
                                font=theme.BODY, fg_color="transparent",
                                text_color="#D7E7E3", hover_color="#1C4A42",
                                corner_radius=8,
                                command=lambda k=key: self.show_page(k))
            btn.pack(fill="x", padx=14, pady=2)
            self.buttons[key] = btn

        bottom = ctk.CTkFrame(bar, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=14, pady=20)
        ctk.CTkLabel(bottom, text=f"Connecté : {self.user['username']}", font=theme.SMALL,
                     text_color="#8FB8AE").pack(anchor="w", padx=10, pady=(0, 8))
        ctk.CTkButton(bottom, text="Se déconnecter", height=36, fg_color="#1C4A42",
                      hover_color="#26605A", command=self.on_logout).pack(fill="x")

    def show_page(self, key):
        if self.active:
            self.pages[self.active].pack_forget()
            self.buttons[self.active].configure(fg_color="transparent")
        if key not in self.pages:
            view_class = next(p[3] for p in PAGES if p[0] == key)
            self.pages[key] = view_class(self.content, self.user, app=self)
        self.pages[key].pack(fill="both", expand=True)
        self.buttons[key].configure(fg_color=theme.PRIMARY)
        self.active = key
        self.pages[key].refresh()

    def on_theme_changed(self):
        """Appelé par les paramètres : met à jour tableaux et graphiques."""
        theme.apply_treeview_style()
        for page in self.pages.values():
            if hasattr(page, "on_theme_changed"):
                page.on_theme_changed()
