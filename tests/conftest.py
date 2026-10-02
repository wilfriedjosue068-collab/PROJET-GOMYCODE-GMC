"""Fixtures communes : chaque test travaille sur une base SQLite en mémoire."""
import pytest

from database import db
from services import auth_service, category_service


@pytest.fixture(autouse=True)
def memory_db():
    db.init_db(":memory:")
    yield
    db.close_db()


@pytest.fixture
def user_id():
    return auth_service.register("testeur", "secret123")


@pytest.fixture
def cats(user_id):
    """Dictionnaire {nom de catégorie: id}."""
    return {c["name"]: c["id"] for c in category_service.list_categories(user_id)}
