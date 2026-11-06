# TP CCFL - prêt de matériel

Tout se lance depuis 	p-ccfl/.

`
cp .env.example .env
uv sync
docker compose up -d   # Postgres pour plus tard, pas besoin avant l'étape 4
uv run python etape01/exploration.py
uv run python etape02/analyse_pandas.py
uv run python etape03/qualite.py
`

Les CSV et le rapport partent dans sorties/.
