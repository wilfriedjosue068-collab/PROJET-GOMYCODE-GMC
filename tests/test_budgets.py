import pytest

from services import budget_service as bs
from services import transaction_service as ts


def test_budget_status_levels(user_id, cats):
    bs.set_budget(user_id, cats["Transport"], "2026-09", 20000)
    bs.set_budget(user_id, cats["Alimentation"], "2026-09", 50000)
    bs.set_budget(user_id, cats["Loisirs"], "2026-09", 10000)
    ts.add_transaction(user_id, cats["Transport"], 25000, "10/09/2026")      # 125 %
    ts.add_transaction(user_id, cats["Alimentation"], 42000, "10/09/2026")   # 84 %
    ts.add_transaction(user_id, cats["Loisirs"], 1000, "10/09/2026")         # 10 %
    ts.add_transaction(user_id, cats["Transport"], 99000, "10/08/2026")      # autre mois
    status = {b["category"]: b for b in bs.get_budget_status(user_id, "2026-09")}
    assert status["Transport"]["level"] == "danger"
    assert status["Transport"]["remaining"] == -5000
    assert status["Alimentation"]["level"] == "warning"
    assert status["Loisirs"]["level"] == "ok"
    alerts = bs.check_overruns(user_id, "2026-09")
    assert [a["category"] for a in alerts] == ["Transport", "Alimentation"]


def test_set_budget_updates_existing(user_id, cats):
    bs.set_budget(user_id, cats["Transport"], "2026-09", 20000)
    bs.set_budget(user_id, cats["Transport"], "2026-09", 30000)
    status = bs.get_budget_status(user_id, "2026-09")
    assert len(status) == 1 and status[0]["budget"] == 30000


def test_budget_on_income_category_rejected(user_id, cats):
    with pytest.raises(ValueError, match="dépense"):
        bs.set_budget(user_id, cats["Salaire"], "2026-09", 1000)


def test_copy_budgets(user_id, cats):
    bs.set_budget(user_id, cats["Transport"], "2026-08", 20000)
    bs.set_budget(user_id, cats["Logement"], "2026-08", 120000)
    assert bs.copy_budgets(user_id, "2026-08", "2026-09") == 2
    assert len(bs.get_budget_status(user_id, "2026-09")) == 2
