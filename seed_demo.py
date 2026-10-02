"""Crée un compte de démonstration avec 6 mois de données réalistes.

Utilisation : python seed_demo.py
Identifiants : demo / demo1234
"""
import random
from datetime import date

from database import db
from services import (auth_service, budget_service, category_service, report_service,
                      transaction_service)
from utils.dates import current_month, month_bounds, shift_month

USERNAME, PASSWORD = "demo", "demo1234"

# (catégorie, description, montant min, montant max, nb par mois)
RECURRING_EXPENSES = [
    ("Alimentation", ["Marché de Treichville", "Supermarché", "Boutique du quartier",
                      "Poisson frais", "Attiéké et garba"], 3000, 15000, 9),
    ("Transport", ["Woro-woro", "Taxi compteur", "Gbaka", "Carburant"], 1000, 6000, 10),
    ("Communication", ["Recharge mobile", "Forfait internet"], 2000, 10000, 2),
    ("Loisirs", ["Maquis entre amis", "Cinéma", "Sortie plage"], 3000, 15000, 2),
    ("Famille", ["Aide aux parents", "Cérémonie familiale"], 10000, 30000, 1),
]


def seed():
    db.init_db()
    if auth_service.login(USERNAME, PASSWORD):
        print("Le compte de démonstration existe déjà (demo / demo1234).")
        return
    uid = auth_service.register(USERNAME, PASSWORD)
    cats = {c["name"]: c["id"] for c in category_service.list_categories(uid)}
    rng = random.Random(2026)
    today = date.today()
    this_month = current_month()

    def add(cat, amount, day, month, desc=""):
        d = date.fromisoformat(f"{month}-{day:02d}")
        if d <= today:
            transaction_service.add_transaction(uid, cats[cat], amount, d, desc)

    for offset in range(5, -1, -1):
        month = shift_month(this_month, -offset)
        last_day = int(month_bounds(month)[1][-2:])
        add("Salaire", 450000, 20, month, "Salaire mensuel")
        if offset in (2, 4):
            add("Activité secondaire", rng.choice([60000, 85000]), 15, month,
                "Prestation informatique")
        add("Logement", 120000, 5, month, "Loyer")
        add("Électricité & eau", rng.randrange(18000, 30000, 500), 12, month, "Facture CIE / SODECI")
        if offset % 2 == 0:
            add("Santé", rng.randrange(5000, 25000, 500), rng.randint(1, 25), month, "Pharmacie")
        for cat, descs, low, high, count in RECURRING_EXPENSES:
            for _ in range(count):
                add(cat, rng.randrange(low, high, 500), rng.randint(1, last_day), month,
                    rng.choice(descs))

    # Budgets : reconduits sur les 2 derniers mois, avec une alerte visible ce mois-ci
    spent = dict(report_service.get_expenses_by_category(uid, this_month))
    budgets = {
        "Logement": 150000,
        "Électricité & eau": 40000,
        "Communication": 25000,
        "Alimentation": round(spent.get("Alimentation", 60000) / 0.85, -3),   # ~85 % : attention
        "Transport": round(spent.get("Transport", 30000) * 0.88, -3),         # dépassé
        "Loisirs": 30000,
    }
    for name, amount in budgets.items():
        budget_service.set_budget(uid, cats[name], shift_month(this_month, -1), amount)
        budget_service.set_budget(uid, cats[name], this_month, amount)

    count = len(transaction_service.list_transactions(uid))
    print(f"Compte de démonstration créé : {USERNAME} / {PASSWORD} ({count} transactions).")


if __name__ == "__main__":
    seed()
