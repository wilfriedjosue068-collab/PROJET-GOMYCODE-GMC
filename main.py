"""Point d'entrée de MoneyTrack : python main.py"""
import customtkinter as ctk

from database.db import close_db, init_db
from ui.app import MoneyTrackApp


def main():
    init_db()
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
    app = MoneyTrackApp()
    try:
        app.mainloop()
    finally:
        close_db()


if __name__ == "__main__":
    main()
