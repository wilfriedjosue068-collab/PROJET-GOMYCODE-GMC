"""UC2 - Gestion des catégories de revenus et de dépenses."""
import unicodedata

import config
from database.db import get_connection
from utils.validators import validate_category_name, validate_type


def create_default_categories(user_id):
    """Crée les catégories de base pour un nouvel utilisateur."""
    conn = get_connection()
    for type_, names in config.DEFAULT_CATEGORIES.items():
        conn.executemany(
            "INSERT OR IGNORE INTO categories (user_id, name, type) VALUES (?, ?, ?)",
            [(user_id, name, type_) for name in names],
        )
    conn.commit()


def list_categories(user_id, type_=None):
    """Liste les catégories de l'utilisateur, triées par nom."""
    sql = "SELECT id, name, type FROM categories WHERE user_id = ?"
    params = [user_id]
    if type_:
        sql += " AND type = ?"
        params.append(validate_type(type_))
    rows = [dict(r) for r in get_connection().execute(sql, params)]
    return sorted(rows, key=lambda c: _sort_key(c["name"]))


def _sort_key(name):
    """Tri alphabétique qui ignore les accents (Électricité rangé avec les E)."""
    return unicodedata.normalize("NFD", name.lower()).encode("ascii", "ignore")


def get_category(category_id, user_id):
    row = get_connection().execute(
        "SELECT id, name, type FROM categories WHERE id = ? AND user_id = ?",
        (category_id, user_id),
    ).fetchone()
    return dict(row) if row else None


def _ensure_unique(user_id, name, type_, exclude_id=None):
    row = get_connection().execute(
        "SELECT id FROM categories WHERE user_id = ? AND name = ? AND type = ?",
        (user_id, name, type_),
    ).fetchone()
    if row and row["id"] != exclude_id:
        raise ValueError(f"La catégorie « {name} » existe déjà.")


def add_category(user_id, name, type_):
    """Ajoute une catégorie. Retourne son id."""
    name = validate_category_name(name)
    type_ = validate_type(type_)
    _ensure_unique(user_id, name, type_)
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)",
        (user_id, name, type_),
    )
    conn.commit()
    return cursor.lastrowid


def rename_category(category_id, user_id, new_name):
    """Renomme une catégorie existante."""
    category = get_category(category_id, user_id)
    if category is None:
        raise ValueError("Catégorie introuvable.")
    new_name = validate_category_name(new_name)
    _ensure_unique(user_id, new_name, category["type"], exclude_id=category_id)
    conn = get_connection()
    conn.execute("UPDATE categories SET name = ? WHERE id = ?", (new_name, category_id))
    conn.commit()
    return True


def delete_category(category_id, user_id):
    """Supprime une catégorie si aucune transaction ne l'utilise."""
    if get_category(category_id, user_id) is None:
        raise ValueError("Catégorie introuvable.")
    conn = get_connection()
    used = conn.execute(
        "SELECT COUNT(*) FROM transactions WHERE category_id = ?", (category_id,)
    ).fetchone()[0]
    if used:
        raise ValueError(
            f"Impossible de supprimer : cette catégorie est utilisée par {used} transaction(s)."
        )
    conn.execute("DELETE FROM budgets WHERE category_id = ?", (category_id,))
    conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    return True
