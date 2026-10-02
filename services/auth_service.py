"""UC1 - Inscription, connexion et changement de mot de passe."""
import hashlib
import secrets

from database.db import get_connection
from services import category_service
from utils.validators import validate_password, validate_username

_ITERATIONS = 200_000


def _hash_password(password, salt):
    """Hache le mot de passe avec PBKDF2-SHA256 et un sel aléatoire."""
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                 bytes.fromhex(salt), _ITERATIONS)
    return digest.hex()


def register(username, password, confirm=None):
    """Crée un compte et ses catégories par défaut. Retourne l'id du nouvel utilisateur."""
    username = validate_username(username)
    validate_password(password)
    if confirm is not None and confirm != password:
        raise ValueError("Les deux mots de passe ne correspondent pas.")

    conn = get_connection()
    if conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone():
        raise ValueError("Ce nom d'utilisateur est déjà utilisé.")

    salt = secrets.token_hex(16)
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
        (username, _hash_password(password, salt), salt),
    )
    conn.commit()
    user_id = cursor.lastrowid
    category_service.create_default_categories(user_id)
    return user_id


def login(username, password):
    """Vérifie les identifiants. Retourne {'id', 'username'} ou None."""
    row = get_connection().execute(
        "SELECT id, username, password_hash, salt FROM users WHERE username = ?",
        (str(username or "").strip(),),
    ).fetchone()
    if row is None or not password:
        return None
    if not secrets.compare_digest(_hash_password(password, row["salt"]), row["password_hash"]):
        return None
    return {"id": row["id"], "username": row["username"]}


def change_password(user_id, old_password, new_password, confirm=None):
    """Change le mot de passe après vérification de l'ancien."""
    conn = get_connection()
    row = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None or login(row["username"], old_password) is None:
        raise ValueError("L'ancien mot de passe est incorrect.")
    validate_password(new_password)
    if confirm is not None and confirm != new_password:
        raise ValueError("Les deux mots de passe ne correspondent pas.")
    salt = secrets.token_hex(16)
    conn.execute("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                 (_hash_password(new_password, salt), salt, user_id))
    conn.commit()
    return True
