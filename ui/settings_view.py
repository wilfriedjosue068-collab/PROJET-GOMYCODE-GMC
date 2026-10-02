"""Paramètres : thème d'affichage, mot de passe, à propos."""
import customtkinter as ctk

import config
from services import auth_service
from ui import theme
from ui.widgets import Card, labeled_entry, page_header, primary_button, show_error, show_info

THEMES = {"Clair": "light", "Sombre": "dark", "Système": "system"}


class SettingsView(ctk.CTkFrame):
    def __init__(self, master, user, app=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.app = app
        page_header(self, "Paramètres")

        appearance = Card(self)
        appearance.pack(fill="x", padx=28)
        ctk.CTkLabel(appearance, text="Apparence", font=theme.SUBTITLE,
                     anchor="w").pack(fill="x", padx=16, pady=(12, 6))
        self.theme_switch = ctk.CTkSegmentedButton(
            appearance, values=list(THEMES), command=self.change_theme,
            selected_color=theme.PRIMARY, selected_hover_color=theme.PRIMARY_HOVER)
        current = ctk.get_appearance_mode()
        self.theme_switch.set("Sombre" if current == "Dark" else "Clair")
        self.theme_switch.pack(anchor="w", padx=16, pady=(0, 14))

        security = Card(self)
        security.pack(fill="x", padx=28, pady=14)
        ctk.CTkLabel(security, text="Changer le mot de passe", font=theme.SUBTITLE,
                     anchor="w").pack(fill="x", padx=16, pady=(12, 6))
        row = ctk.CTkFrame(security, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 14))
        self.old_pwd = labeled_entry(row, "Mot de passe actuel", 200, show="•")
        self.old_pwd.container.pack(side="left", padx=(0, 10))
        self.new_pwd = labeled_entry(row, "Nouveau mot de passe", 200, show="•")
        self.new_pwd.container.pack(side="left", padx=(0, 10))
        self.confirm_pwd = labeled_entry(row, "Confirmation", 200, show="•")
        self.confirm_pwd.container.pack(side="left", padx=(0, 10))
        primary_button(row, "Mettre à jour", self.change_password,
                       width=140).pack(side="left", anchor="s")

        about = Card(self)
        about.pack(fill="x", padx=28)
        ctk.CTkLabel(about, text="À propos", font=theme.SUBTITLE,
                     anchor="w").pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(about, justify="left", anchor="w", font=theme.BODY,
                     text_color=theme.MUTED,
                     text=f"{config.APP_NAME} version {config.APP_VERSION}\n"
                          "Application de gestion budgétaire personnelle - projet de "
                          "fin de formation Python essentiel.\n"
                          f"Base de données : {config.DB_PATH}"
                     ).pack(fill="x", padx=16, pady=(0, 14))

    def refresh(self):
        pass

    def change_theme(self, choice):
        ctk.set_appearance_mode(THEMES[choice])
        if self.app is not None:
            self.after(50, self.app.on_theme_changed)

    def change_password(self):
        try:
            auth_service.change_password(self.user["id"], self.old_pwd.get(),
                                         self.new_pwd.get(), self.confirm_pwd.get())
        except ValueError as exc:
            show_error(str(exc))
            return
        for entry in (self.old_pwd, self.new_pwd, self.confirm_pwd):
            entry.delete(0, "end")
        show_info("Mot de passe mis à jour.")
