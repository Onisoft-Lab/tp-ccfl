# Raccourcis pour lancer les étapes depuis la racine

.PHONY: sync db etape1 etape2 etape3 all

sync:
	uv sync

db:
	docker compose up -d

etape1:
	uv run python etape01/exploration.py

etape2:
	uv run python etape02/analyse_pandas.py

etape3:
	uv run python etape03/qualite.py

all: etape1 etape2 etape3
