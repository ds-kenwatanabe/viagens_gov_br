import argparse
import logging
import os
import time
from collections.abc import Iterator
from decimal import Decimal

import requests

from src.config import load_settings
from src.database import connect_db
from src.extract_locations import extract_locations


LOGGER = logging.getLogger(__name__)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def ensure_geocode_schema(conn) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS viagem_localidades (
                id SERIAL PRIMARY KEY,
                viagem_id INTEGER REFERENCES viagens(id),
                local_texto TEXT,
                cidade TEXT,
                estado TEXT,
                pais TEXT,
                latitude NUMERIC,
                longitude NUMERIC,
                confidence NUMERIC,
                fonte TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE (viagem_id, local_texto)
            );

            CREATE INDEX IF NOT EXISTS idx_viagem_localidades_viagem_id
                ON viagem_localidades (viagem_id);

            CREATE INDEX IF NOT EXISTS idx_viagem_localidades_geo
                ON viagem_localidades (latitude, longitude);
            """
        )
    conn.commit()


def run_geocoding(limit: int = 100, delay_seconds: float = 1.0) -> int:
    settings = load_settings()
    user_agent = os.getenv("NOMINATIM_USER_AGENT")
    if not user_agent:
        raise RuntimeError("Defina NOMINATIM_USER_AGENT no .env antes de geocodificar.")

    conn = connect_db(settings)
    try:
        ensure_geocode_schema(conn)
        inserted = 0
        cache: dict[str, tuple[Decimal | None, Decimal | None, Decimal | None]] = {}

        for trip in _iter_trips(conn, limit):
            for location in extract_locations(trip["motivo"]):
                local_texto = location["local_texto"]
                if _location_exists(conn, trip["id"], local_texto):
                    continue

                lat, lon, confidence = _geocode_location(location, user_agent, cache)
                _insert_location(conn, trip["id"], location, lat, lon, confidence)
                inserted += 1
                if lat is not None and lon is not None:
                    time.sleep(delay_seconds)

        conn.commit()
        LOGGER.info("Geocodificacao finalizada. Localidades inseridas=%s", inserted)
        return inserted
    finally:
        conn.close()


def _iter_trips(conn, limit: int) -> Iterator[dict]:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT v.id, v.motivo
              FROM viagens v
             WHERE v.motivo IS NOT NULL
               AND NOT EXISTS (
                   SELECT 1
                     FROM viagem_localidades l
                    WHERE l.viagem_id = v.id
               )
             ORDER BY v.data_inicio_afastamento DESC NULLS LAST, v.id DESC
             LIMIT %s
            """,
            (limit,),
        )
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            yield dict(zip(columns, row))


def _location_exists(conn, viagem_id: int, local_texto: str) -> bool:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1
                  FROM viagem_localidades
                 WHERE viagem_id = %s
                   AND local_texto = %s
            )
            """,
            (viagem_id, local_texto),
        )
        return bool(cursor.fetchone()[0])


def _geocode_location(
    location: dict[str, str | None],
    user_agent: str,
    cache: dict[str, tuple[Decimal | None, Decimal | None, Decimal | None]],
) -> tuple[Decimal | None, Decimal | None, Decimal | None]:
    query = ", ".join(
        value
        for value in [location["cidade"], location["estado"], location["pais"]]
        if value
    )
    if query in cache:
        return cache[query]

    response = requests.get(
        NOMINATIM_URL,
        params={"q": query, "format": "jsonv2", "limit": 1},
        headers={"User-Agent": user_agent},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if not data:
        result = (None, None, Decimal("0"))
    else:
        item = data[0]
        result = (
            Decimal(str(item["lat"])),
            Decimal(str(item["lon"])),
            Decimal(str(item.get("importance", 0))),
        )

    cache[query] = result
    return result


def _insert_location(
    conn,
    viagem_id: int,
    location: dict[str, str | None],
    latitude: Decimal | None,
    longitude: Decimal | None,
    confidence: Decimal | None,
) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO viagem_localidades (
                viagem_id, local_texto, cidade, estado, pais,
                latitude, longitude, confidence, fonte
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (viagem_id, local_texto) DO NOTHING
            """,
            (
                viagem_id,
                location["local_texto"],
                location["cidade"],
                location["estado"],
                location["pais"],
                latitude,
                longitude,
                confidence,
                "nominatim",
            ),
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extrai e geocodifica localidades de viagens.")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--delay-seconds", type=float, default=1.0)
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_geocoding(limit=args.limit, delay_seconds=args.delay_seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
