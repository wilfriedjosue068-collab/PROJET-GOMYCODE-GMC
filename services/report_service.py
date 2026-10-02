"""UC8 - Données du tableau de bord et des rapports."""
from database.db import get_connection
from utils.dates import shift_month
from utils.validators import validate_month


def get_monthly_summary(user_id, month):
    """Total des revenus, des dépenses et solde d'un mois."""
    month = validate_month(month)
    row = get_connection().execute(
        """
        SELECT COALESCE(SUM(CASE WHEN c.type = 'revenu'  THEN t.amount END), 0) AS revenus,
               COALESCE(SUM(CASE WHEN c.type = 'depense' THEN t.amount END), 0) AS depenses,
               COUNT(t.id) AS nb
        FROM transactions t JOIN categories c ON c.id = t.category_id
        WHERE t.user_id = ? AND substr(t.date, 1, 7) = ?
        """,
        (user_id, month),
    ).fetchone()
    return {
        "revenus": row["revenus"],
        "depenses": row["depenses"],
        "solde": row["revenus"] - row["depenses"],
        "nb_transactions": row["nb"],
    }


def get_global_balance(user_id):
    """Solde cumulé depuis la première transaction."""
    row = get_connection().execute(
        """
        SELECT COALESCE(SUM(CASE WHEN c.type = 'revenu' THEN t.amount ELSE -t.amount END), 0)
        FROM transactions t JOIN categories c ON c.id = t.category_id
        WHERE t.user_id = ?
        """,
        (user_id,),
    ).fetchone()
    return row[0]


def get_expenses_by_category(user_id, month):
    """Répartition des dépenses du mois par catégorie : [(nom, total), ...] décroissant."""
    rows = get_connection().execute(
        """
        SELECT c.name, SUM(t.amount) AS total
        FROM transactions t JOIN categories c ON c.id = t.category_id
        WHERE t.user_id = ? AND c.type = 'depense' AND substr(t.date, 1, 7) = ?
        GROUP BY c.id ORDER BY total DESC
        """,
        (user_id, validate_month(month)),
    ).fetchall()
    return [(r["name"], r["total"]) for r in rows]


def get_monthly_trend(user_id, end_month, months=6):
    """Revenus et dépenses des `months` derniers mois jusqu'à `end_month` inclus."""
    end_month = validate_month(end_month)
    return [
        {"month": m, **get_monthly_summary(user_id, m)}
        for m in (shift_month(end_month, -i) for i in range(months - 1, -1, -1))
    ]
