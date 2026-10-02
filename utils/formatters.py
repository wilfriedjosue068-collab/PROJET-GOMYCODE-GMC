"""Mise en forme des montants et des dates pour l'affichage."""
from datetime import datetime

import config


def format_amount(amount, with_currency=True, signed=False):
    """137500 -> '137 500 FCFA'."""
    value = int(round(amount or 0))
    text = f"{abs(value):,}".replace(",", " ")
    if value < 0:
        text = "-" + text
    elif signed and value > 0:
        text = "+" + text
    return f"{text} {config.CURRENCY}" if with_currency else text


def format_date(iso_date):
    """'2026-09-23' -> '23/09/2026'."""
    if not iso_date:
        return ""
    return datetime.strptime(iso_date, "%Y-%m-%d").strftime("%d/%m/%Y")


def format_percent(ratio):
    return f"{ratio * 100:.0f} %"


def type_label(type_):
    return "Revenu" if type_ == "revenu" else "Dépense"
