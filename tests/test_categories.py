import pytest

from services import category_service, transaction_service


def test_add_and_rename_category(user_id):
    cat_id = category_service.add_category(user_id, "  Cotisations   tontine ", "depense")
    assert category_service.get_category(cat_id, user_id)["name"] == "Cotisations tontine"
    category_service.rename_category(cat_id, user_id, "Tontine")
    assert category_service.get_category(cat_id, user_id)["name"] == "Tontine"


def test_duplicate_category_rejected(user_id):
    with pytest.raises(ValueError, match="existe déjà"):
        category_service.add_category(user_id, "transport", "depense")


def test_same_name_allowed_for_other_type(user_id):
    assert category_service.add_category(user_id, "Transport", "revenu")


def test_cannot_delete_used_category(user_id, cats):
    transaction_service.add_transaction(user_id, cats["Transport"], 2000, "01/09/2026")
    with pytest.raises(ValueError, match="utilisée"):
        category_service.delete_category(cats["Transport"], user_id)


def test_delete_unused_category(user_id, cats):
    assert category_service.delete_category(cats["Loisirs"], user_id)
    assert category_service.get_category(cats["Loisirs"], user_id) is None


def test_categories_are_private_to_user(user_id, cats):
    from services import auth_service
    other = auth_service.register("autre", "secret123")
    assert category_service.get_category(cats["Transport"], other) is None
