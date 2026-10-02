"""Écran de connexion / inscription (UC1)."""
import customtkinter as ctk

import config
from services import auth_service
from ui import theme
from ui.widgets import Card, labeled_entry, primary_button


class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_success):
        super().__init__(master, fg_color=theme.BG, corner_radius=0)
        self.on_success = on_success

        card = Card(self, width=420)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text=config.APP_NAME, font=(theme.FONT, 30, "bold"),
                     text_color=theme.PRIMARY).pack(pady=(30, 0))
        ctk.CTkLabel(card, text="Prenez le contrôle de votre budget", font=theme.BODY,
                     text_color=theme.MUTED).pack(pady=(0, 10))

        tabs = ctk.CTkTabview(card, width=360, height=330, fg_color="transparent",
                              segmented_button_selected_color=theme.PRIMARY,
                              segmented_button_selected_hover_color=theme.PRIMARY_HOVER)
        tabs.pack(padx=30, pady=(0, 24))
        self._build_login(tabs.add("Connexion"))
        self._build_register(tabs.add("Inscription"))

    def _build_login(self, tab):
        self.login_user = labeled_entry(tab, "Nom d'utilisateur", 300)
        self.login_user.container.pack(fill="x", pady=(10, 8))
        self.login_pwd = labeled_entry(tab, "Mot de passe", 300, show="•")
        self.login_pwd.container.pack(fill="x", pady=8)
        self.login_msg = ctk.CTkLabel(tab, text="", text_color=theme.EXPENSE, font=theme.SMALL)
        self.login_msg.pack(pady=(4, 0))
        primary_button(tab, "Se connecter", self.do_login, width=300).pack(pady=12)
        for entry in (self.login_user, self.login_pwd):
            entry.bind("<Return>", lambda e: self.do_login())
        self.after(200, self.login_user.focus_set)

    def _build_register(self, tab):
        self.reg_user = labeled_entry(tab, "Nom d'utilisateur", 300)
        self.reg_user.container.pack(fill="x", pady=(10, 6))
        self.reg_pwd = labeled_entry(tab, "Mot de passe (6 caractères min.)", 300, show="•")
        self.reg_pwd.container.pack(fill="x", pady=6)
        self.reg_confirm = labeled_entry(tab, "Confirmer le mot de passe", 300, show="•")
        self.reg_confirm.container.pack(fill="x", pady=6)
        self.reg_msg = ctk.CTkLabel(tab, text="", text_color=theme.EXPENSE, font=theme.SMALL,
                                    wraplength=300)
        self.reg_msg.pack()
        primary_button(tab, "Créer mon compte", self.do_register, width=300).pack(pady=8)

    def do_login(self):
        user = auth_service.login(self.login_user.get(), self.login_pwd.get())
        if user is None:
            self.login_msg.configure(text="Nom d'utilisateur ou mot de passe incorrect.")
            return
        self.on_success(user)

    def do_register(self):
        try:
            auth_service.register(self.reg_user.get(), self.reg_pwd.get(), self.reg_confirm.get())
        except ValueError as exc:
            self.reg_msg.configure(text=str(exc))
            return
        self.on_success(auth_service.login(self.reg_user.get(), self.reg_pwd.get()))
