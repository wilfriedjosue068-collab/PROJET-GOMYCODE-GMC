"""UC6 et UC7 - Budgets mensuels par catégorie et alertes de dépassement."""
import config
from database.db import get_connection
from services.category_service import get_category
from utils.validators import validate_amount, validate_month


def set_budget(user_id, category_id, month, amount):
    """UC6 - Crée ou met à jour le budget d'une catégorie de dépense pour un mois."""
    category = get_category(category_id, user_id)
    if category is None:
        raise ValueError("Catégorie introuvable.")
    if category["type"] != "depense":
        raise ValueError("Un budget ne peut être défini que sur une catégorie de dépense.")
    month = validate_month(month)
    amount = validate_amount(amount)
    conn = get_connection()
    conn.execute(
        "INSERT INTO budgets (user_id, category_id, month, amount) VALUES (?, ?, ?, ?) "
        "ON CONFLICT (user_id, category_id, month) DO UPDATE SET amount = excluded.amount",
        (user_id, category_id, month, amount),
    )
    conn.commit()
    return True


def delete_budget(user_id, category_id, month):
    conn = get_connection()
    cursor = conn.execute(
        "DELETE FROM budgets WHERE user_id = ? AND category_id = ? AND month = ?",
        (user_id, category_id, validate_month(month)),
    )
    conn.commit()
    return cursor.rowcount > 0


def _level(ratio):
    if ratio > 1:
        return "danger"
    if ratio >= config.BUDGET_WARNING_RATIO:
        return "warning"
    return "ok"


def get_budget_status(user_id, month):
    """Pour chaque budget du mois : montant prévu, dépensé, reste, taux et niveau d'alerte."""
    month = validate_month(month)
    rows = get_connection().execute(
        """
        SELECT b.category_id, c.name AS category, b.amount AS budget,
               COALESCE((SELECT SUM(t.amount) FROM transactions t
                         WHERE t.user_id = b.user_id AND t.category_id = b.category_id
                           AND substr(t.date, 1, 7) = b.month), 0) AS spent
        FROM budgets b
        JOIN categories c ON c.id = b.category_id
        WHERE b.user_id = ? AND b.month = ?
        ORDER BY c.name COLLATE NOCASE
        """,
        (user_id, month),
    ).fetchall()
    result = []
    for r in rows:
        ratio = r["spent"] / r["budget"]
        result.append({
            "category_id": r["category_id"],
            "category": r["category"],
            "budget": r["budget"],
            "spent": r["spent"],
            "remaining": r["budget"] - r["spent"],
            "ratio": ratio,
            "level": _level(ratio),
        })
    return result


def check_overruns(user_id, month):
    """UC7 - Budgets dépassés ou proches du dépassement, les plus critiques d'abord."""
    alerts = [b for b in get_budget_status(user_id, month) if b["level"] != "ok"]
    return sorted(alerts, key=lambda b: b["ratio"], reverse=True)


def copy_budgets(user_id, from_month, to_month):
    """Reconduit les budgets d'un mois vers un autre (sans écraser l'existant)."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT OR IGNORE INTO budgets (user_id, category_id, month, amount) "
        "SELECT user_id, category_id, ?, amount FROM budgets WHERE user_id = ? AND month = ?",
        (validate_month(to_month), user_id, validate_month(from_month)),
    )
    conn.commit()
    return cursor.rowcount
