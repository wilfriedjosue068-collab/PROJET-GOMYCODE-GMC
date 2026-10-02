"""UC3 à UC5 - Enregistrement, modification, suppression et consultation des transactions."""
from database.db import get_connection
from services.category_service import get_category
from utils.validators import validate_amount, validate_date, validate_type

_SELECT = """
    SELECT t.id, t.amount, t.date, t.description, t.category_id,
           c.name AS category, c.type AS type
    FROM transactions t
    JOIN categories c ON c.id = t.category_id
"""


def _check_category(category_id, user_id):
    if get_category(category_id, user_id) is None:
        raise ValueError("Veuillez choisir une catégorie valide.")


def add_transaction(user_id, category_id, amount, date, description=""):
    """UC3 - Enregistre un revenu ou une dépense (le type vient de la catégorie)."""
    _check_category(category_id, user_id)
    amount = validate_amount(amount)
    date = validate_date(date)
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO transactions (user_id, category_id, amount, date, description) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, category_id, amount, date, (description or "").strip()),
    )
    conn.commit()
    return cursor.lastrowid


def update_transaction(transaction_id, user_id, category_id, amount, date, description=""):
    """UC4 - Modifie une transaction existante."""
    if get_transaction(transaction_id, user_id) is None:
        raise ValueError("Transaction introuvable.")
    _check_category(category_id, user_id)
    amount = validate_amount(amount)
    date = validate_date(date)
    conn = get_connection()
    conn.execute(
        "UPDATE transactions SET category_id = ?, amount = ?, date = ?, description = ? "
        "WHERE id = ? AND user_id = ?",
        (category_id, amount, date, (description or "").strip(), transaction_id, user_id),
    )
    conn.commit()
    return True


def delete_transaction(transaction_id, user_id):
    """UC4 - Supprime une transaction. Retourne True si une ligne a été supprimée."""
    conn = get_connection()
    cursor = conn.execute(
        "DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id)
    )
    conn.commit()
    return cursor.rowcount > 0


def get_transaction(transaction_id, user_id):
    row = get_connection().execute(
        _SELECT + " WHERE t.id = ? AND t.user_id = ?", (transaction_id, user_id)
    ).fetchone()
    return dict(row) if row else None


def list_transactions(user_id, start=None, end=None, category_id=None,
                      type_=None, search=None, limit=None):
    """UC5 - Historique filtré, du plus récent au plus ancien."""
    sql = _SELECT + " WHERE t.user_id = ?"
    params = [user_id]
    if start:
        sql += " AND t.date >= ?"
        params.append(validate_date(start))
    if end:
        sql += " AND t.date <= ?"
        params.append(validate_date(end))
    if category_id:
        sql += " AND t.category_id = ?"
        params.append(category_id)
    if type_:
        sql += " AND c.type = ?"
        params.append(validate_type(type_))
    if search and search.strip():
        sql += " AND (t.description LIKE ? OR c.name LIKE ?)"
        pattern = f"%{search.strip()}%"
        params += [pattern, pattern]
    sql += " ORDER BY t.date DESC, t.id DESC"
    if limit:
        sql += " LIMIT ?"
        params.append(int(limit))
    return [dict(r) for r in get_connection().execute(sql, params)]


def compute_totals(transactions):
    """Calcule les totaux revenus / dépenses / solde d'une liste de transactions."""
    income = sum(t["amount"] for t in transactions if t["type"] == "revenu")
    expense = sum(t["amount"] for t in transactions if t["type"] == "depense")
    return {"revenus": income, "depenses": expense, "solde": income - expense}
