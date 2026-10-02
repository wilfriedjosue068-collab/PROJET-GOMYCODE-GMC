import pytest

from services import transaction_service as ts


def test_add_transaction(user_id, cats):
    tid = ts.add_transaction(user_id, cats["Alimentation"], "12 500", "15/09/2026", "Marché")
    t = ts.get_transaction(tid, user_id)
    assert t["amount"] == 12500
    assert t["date"] == "2026-09-15"
    assert t["type"] == "depense"
    assert t["category"] == "Alimentation"


@pytest.mark.parametrize("amount", [0, -500, "abc", ""])
def test_invalid_amount_rejected(user_id, cats, amount):
    with pytest.raises(ValueError):
        ts.add_transaction(user_id, cats["Alimentation"], amount, "15/09/2026")


def test_invalid_date_rejected(user_id, cats):
    with pytest.raises(ValueError):
        ts.add_transaction(user_id, cats["Alimentation"], 1000, "31/02/2026")


def test_update_and_delete(user_id, cats):
    tid = ts.add_transaction(user_id, cats["Transport"], 1500, "2026-09-01")
    ts.update_transaction(tid, user_id, cats["Alimentation"], 3000, "02/09/2026", "Pain")
    t = ts.get_transaction(tid, user_id)
    assert (t["amount"], t["category"], t["description"]) == (3000, "Alimentation", "Pain")
    assert ts.delete_transaction(tid, user_id)
    assert ts.get_transaction(tid, user_id) is None


def test_filters(user_id, cats):
    ts.add_transaction(user_id, cats["Salaire"], 450000, "28/08/2026", "Salaire août")
    ts.add_transaction(user_id, cats["Transport"], 2000, "02/09/2026", "Taxi")
    ts.add_transaction(user_id, cats["Alimentation"], 8000, "05/09/2026", "Supermarché")
    assert len(ts.list_transactions(user_id)) == 3
    assert len(ts.list_transactions(user_id, start="01/09/2026")) == 2
    assert len(ts.list_transactions(user_id, type_="revenu")) == 1
    assert len(ts.list_transactions(user_id, category_id=cats["Transport"])) == 1
    assert ts.list_transactions(user_id, search="super")[0]["amount"] == 8000
    # tri : plus récent d'abord
    assert ts.list_transactions(user_id)[0]["date"] == "2026-09-05"


def test_compute_totals(user_id, cats):
    ts.add_transaction(user_id, cats["Salaire"], 450000, "28/08/2026")
    ts.add_transaction(user_id, cats["Transport"], 2000, "02/09/2026")
    totals = ts.compute_totals(ts.list_transactions(user_id))
    assert totals == {"revenus": 450000, "depenses": 2000, "solde": 448000}
