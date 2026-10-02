"""Petites fonctions de manipulation des dates et des mois (format AAAA-MM)."""
import calendar
from datetime import date

MONTHS_FR = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]
MONTHS_FR_SHORT = [
    "Janv", "Févr", "Mars", "Avr", "Mai", "Juin",
    "Juil", "Août", "Sept", "Oct", "Nov", "Déc",
]


def current_month():
    return date.today().strftime("%Y-%m")


def shift_month(month, delta):
    """shift_month('2026-01', -1) -> '2025-12'."""
    year, mon = map(int, month.split("-"))
    index = year * 12 + (mon - 1) + delta
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def month_label(month, short=False):
    """'2026-09' -> 'Septembre 2026' (ou 'Sept 26' si short=True)."""
    year, mon = map(int, month.split("-"))
    if short:
        return f"{MONTHS_FR_SHORT[mon - 1]} {str(year)[2:]}"
    return f"{MONTHS_FR[mon - 1]} {year}"


def month_bounds(month):
    """Retourne le premier et le dernier jour du mois au format ISO."""
    year, mon = map(int, month.split("-"))
    last_day = calendar.monthrange(year, mon)[1]
    return f"{month}-01", f"{month}-{last_day:02d}"


def today_ui():
    return date.today().strftime("%d/%m/%Y")
