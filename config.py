"""Paramètres globaux de l'application MoneyTrack."""
from pathlib import Path

APP_NAME = "MoneyTrack"
APP_VERSION = "1.0.0"
CURRENCY = "FCFA"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "moneytrack.db"

# Seuil à partir duquel un budget passe en "attention" (80 % consommé)
BUDGET_WARNING_RATIO = 0.8

TRANSACTION_TYPES = ("revenu", "depense")

# Catégories créées automatiquement pour chaque nouvel utilisateur
DEFAULT_CATEGORIES = {
    "revenu": ["Salaire", "Prime", "Activité secondaire", "Autres revenus"],
    "depense": [
        "Alimentation", "Transport", "Logement", "Électricité & eau",
        "Communication", "Santé", "Éducation", "Loisirs", "Famille",
        "Autres dépenses",
    ],
}
