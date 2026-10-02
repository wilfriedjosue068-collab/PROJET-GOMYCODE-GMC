"""Fonctions de validation des saisies utilisateur.

Chaque fonction retourne la valeur nettoyée ou lève ValueError
avec un message en français, directement affichable dans l'interface.
"""
import re
from datetime import date, datetime

import config

_USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{3,30}$")
_MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
MAX_AMOUNT = 1_000_000_000_000


def validate_amount(value):
    """Convertit '12 500', '12500 FCFA' ou 12500 en entier strictement positif."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        number = float(value)
    else:
        text = str(value or "").upper().replace("FCFA", "")
        text = text.replace("\u00a0", "").replace("\u202f", "").replace(" ", "")
        text = text.replace(",", ".")
        if not text:
            raise ValueError("Le montant est obligatoire.")
        try:
            number = float(text)
        except ValueError:
            raise ValueError("Le montant doit être un nombre (ex : 12500).") from None
    amount = int(round(number))
    if amount <= 0:
        raise ValueError("Le montant doit être supérieur à zéro.")
    if amount > MAX_AMOUNT:
        raise ValueError("Le montant est trop élevé.")
    return amount


def validate_date(value):
    """Accepte JJ/MM/AAAA, AAAA-MM-JJ ou un objet date ; retourne 'AAAA-MM-JJ'."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value or "").strip()
    if not text:
        raise ValueError("La date est obligatoire.")
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError("Date invalide. Format attendu : JJ/MM/AAAA.")


def validate_month(value):
    """Vérifie un mois au format 'AAAA-MM'."""
    text = str(value or "").strip()
    if not _MONTH_RE.match(text):
        raise ValueError("Mois invalide. Format attendu : AAAA-MM.")
    return text


def validate_username(value):
    text = str(value or "").strip()
    if not _USERNAME_RE.match(text):
        raise ValueError(
            "Le nom d'utilisateur doit contenir 3 à 30 caractères "
            "(lettres, chiffres, point, tiret ou underscore)."
        )
    return text


def validate_password(value):
    if not value or len(value) < 6:
        raise ValueError("Le mot de passe doit contenir au moins 6 caractères.")
    return value


def validate_category_name(value):
    text = " ".join(str(value or "").split())
    if not text:
        raise ValueError("Le nom de la catégorie est obligatoire.")
    if len(text) > 40:
        raise ValueError("Le nom de la catégorie ne doit pas dépasser 40 caractères.")
    return text


def validate_type(value):
    if value not in config.TRANSACTION_TYPES:
        raise ValueError("Le type doit être 'revenu' ou 'depense'.")
    return value
