# TP CCFL - prêt de matériel

Tout se lance depuis p-ccfl/.

```
cp .env.example .env
uv sync          # ou: make sync
docker compose up -d   # Postgres pour plus tard (étape 4+), ou: make db
uv run python etape01/exploration.py   # make etape1
uv run python etape02/analyse_pandas.py  # make etape2
uv run python etape03/qualite.py         # make etape3
```

make all enchaîne les trois étapes. Les CSV et le rapport partent dans sorties/.
