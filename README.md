# MoneyTrack - Gestion budgétaire personnelle

Application de bureau Python (CustomTkinter + SQLite) pour suivre ses revenus et
dépenses, fixer des budgets mensuels par catégorie et visualiser sa situation financière.

## Installation

```bash
python -m venv venv
venv\Scripts\activate            # Windows  (Linux/Mac : source venv/bin/activate)
pip install -r requirements.txt
```

Python 3.10 ou plus récent. Sous Linux, installer aussi `python3-tk`.

## Lancement

```bash
python seed_demo.py    # (facultatif) crée le compte de démo : demo / demo1234
python main.py
```

## Tests

```bash
pytest -v
```

## Structure

```
main.py              point d'entrée
config.py            paramètres globaux
seed_demo.py         données de démonstration
database/db.py       connexion SQLite + schéma
services/            logique métier (une fonction par fonctionnalité)
  auth_service.py          UC1  inscription, connexion, mot de passe
  category_service.py      UC2  catégories
  transaction_service.py   UC3-UC5 transactions et historique
  budget_service.py        UC6-UC7 budgets et alertes
  report_service.py        UC8  tableau de bord et bilans
  export_service.py        UC9  export CSV / Excel
ui/                  interface graphique (une vue par écran)
utils/               validation, formatage, dates
tests/               tests unitaires pytest
```

La couche `ui/` n'accède jamais directement à la base : elle appelle uniquement
les fonctions de `services/`.
