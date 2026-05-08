DATA_INICIO ?= 2024-05-01
DATA_FIM ?= 2026-04-30
ORGAOS ?= 20000,35000
MAX_REQUESTS ?= 100000
GEOCODE_LIMIT ?= 100
GEOCODE_DELAY_SECONDS ?= 1

.PHONY: up ingest geocode down logs

up:
	docker compose up --build

ingest:
	docker compose run --rm backend python -m src.ingest --data-inicio $(DATA_INICIO) --data-fim $(DATA_FIM) --orgaos $(ORGAOS) --max-requests $(MAX_REQUESTS)

geocode:
	docker compose run --rm backend python -m src.geocode --limit $(GEOCODE_LIMIT) --delay-seconds $(GEOCODE_DELAY_SECONDS)

down:
	docker compose down

logs:
	docker compose logs -f
