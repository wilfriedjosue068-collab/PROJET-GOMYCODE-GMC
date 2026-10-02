"""Accès à la base de données SQLite (connexion unique + création du schéma)."""
import sqlite3
from pathlib import Path

import config

_connection = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    salt          TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name    TEXT NOT NULL COLLATE NOCASE,
    type    TEXT NOT NULL CHECK (type IN ('revenu', 'depense')),
    UNIQUE (user_id, name, type)
);

CREATE TABLE IF NOT EXISTS transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    amount      INTEGER NOT NULL CHECK (amount > 0),
    date        TEXT NOT NULL,              -- format ISO AAAA-MM-JJ
    description TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS budgets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    month       TEXT NOT NULL,              -- format AAAA-MM
    amount      INTEGER NOT NULL CHECK (amount > 0),
    UNIQUE (user_id, category_id, month)
);

CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions (user_id, date);
"""


def init_db(db_path=None):
    """Ouvre la base (fichier ou ':memory:') et crée les tables si besoin."""
    global _connection
    close_db()
    path = str(db_path or config.DB_PATH)
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    _connection = sqlite3.connect(path)
    _connection.row_factory = sqlite3.Row
    _connection.execute("PRAGMA foreign_keys = ON")
    _connection.executescript(SCHEMA)
    _connection.commit()
    return _connection


def get_connection():
    """Retourne la connexion active (l'ouvre au premier appel)."""
    if _connection is None:
        init_db()
    return _connection


def close_db():
    """Ferme proprement la connexion."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
