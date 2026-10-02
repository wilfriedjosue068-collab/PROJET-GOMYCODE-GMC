import pytest

from services import auth_service, category_service


def test_register_and_login(user_id):
    user = auth_service.login("testeur", "secret123")
    assert user == {"id": user_id, "username": "testeur"}


def test_login_is_case_insensitive_on_username(user_id):
    assert auth_service.login("TESTEUR", "secret123")["id"] == user_id


def test_wrong_password_rejected(user_id):
    assert auth_service.login("testeur", "mauvais") is None
    assert auth_service.login("inconnu", "secret123") is None


def test_duplicate_username_rejected(user_id):
    with pytest.raises(ValueError, match="déjà utilisé"):
        auth_service.register("testeur", "autre123")


def test_password_confirmation_must_match():
    with pytest.raises(ValueError, match="correspondent"):
        auth_service.register("alice", "secret123", "secret124")


def test_short_password_rejected():
    with pytest.raises(ValueError):
        auth_service.register("alice", "123")


def test_default_categories_created(user_id):
    names = [c["name"] for c in category_service.list_categories(user_id, "depense")]
    assert "Transport" in names and "Alimentation" in names


def test_change_password(user_id):
    auth_service.change_password(user_id, "secret123", "nouveau456", "nouveau456")
    assert auth_service.login("testeur", "secret123") is None
    assert auth_service.login("testeur", "nouveau456") is not None
    with pytest.raises(ValueError):
        auth_service.change_password(user_id, "faux", "encore789")
