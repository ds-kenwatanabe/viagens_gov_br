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
LOCAL_COORDINATES = {
    ("Brasilia", "DF", "Brasil"): (Decimal("-15.793889"), Decimal("-47.882778")),
    ("Sao Paulo", "SP", "Brasil"): (Decimal("-23.550520"), Decimal("-46.633308")),
    ("Rio de Janeiro", "RJ", "Brasil"): (Decimal("-22.906847"), Decimal("-43.172897")),
    ("Manaus", "AM", "Brasil"): (Decimal("-3.119028"), Decimal("-60.021731")),
    ("Recife", "PE", "Brasil"): (Decimal("-8.047562"), Decimal("-34.877003")),
    ("Salvador", "BA", "Brasil"): (Decimal("-12.977749"), Decimal("-38.501630")),
    ("Fortaleza", "CE", "Brasil"): (Decimal("-3.731862"), Decimal("-38.526669")),
    ("Belem", "PA", "Brasil"): (Decimal("-1.455833"), Decimal("-48.503889")),
    ("Curitiba", "PR", "Brasil"): (Decimal("-25.428954"), Decimal("-49.267137")),
    ("Porto Alegre", "RS", "Brasil"): (Decimal("-30.034647"), Decimal("-51.217658")),
    ("Lisboa", None, "Portugal"): (Decimal("38.722252"), Decimal("-9.139337")),
    ("Washington", "DC", "Estados Unidos"): (Decimal("38.907192"), Decimal("-77.036871")),
    ("Nova York", "NY", "Estados Unidos"): (Decimal("40.712776"), Decimal("-74.005974")),
    ("Paris", None, "Franca"): (Decimal("48.856613"), Decimal("2.352222")),
    ("Londres", None, "Reino Unido"): (Decimal("51.507351"), Decimal("-0.127758")),
    ("Roma", None, "Italia"): (Decimal("41.902782"), Decimal("12.496366")),
    ("Madrid", None, "Espanha"): (Decimal("40.416775"), Decimal("-3.703790")),
    ("Buenos Aires", None, "Argentina"): (Decimal("-34.603722"), Decimal("-58.381592")),
    ("Montevideu", None, "Uruguai"): (Decimal("-34.901113"), Decimal("-56.164531")),
    ("Santiago", None, "Chile"): (Decimal("-33.448890"), Decimal("-70.669265")),
}


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
        LOGGER.warning(
            "NOMINATIM_USER_AGENT nao definido. Usando apenas coordenadas locais conhecidas."
        )

    conn = connect_db(settings)
    try:
        ensure_geocode_schema(conn)
        inserted = 0
        cache: dict[str, tuple[Decimal | None, Decimal | None, Decimal | None, str]] = {}

        for trip in _iter_trips(conn, limit):
            locations = extract_locations(trip["motivo"])
            if not locations:
                _insert_location(
                    conn,
                    trip["id"],
                    {
                        "local_texto": "__NO_LOCATION__",
                        "cidade": None,
                        "estado": None,
                        "pais": None,
                    },
                    None,
                    None,
                    Decimal("0"),
                    "none",
                )
                inserted += 1
                continue

            for location in locations:
                local_texto = location["local_texto"]
                if _location_exists(conn, trip["id"], local_texto):
                    continue

                lat, lon, confidence, source = _geocode_location(
                    location,
                    user_agent,
                    cache,
                    delay_seconds,
                )
                _insert_location(conn, trip["id"], location, lat, lon, confidence, source)
                inserted += 1

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
    user_agent: str | None,
    cache: dict[str, tuple[Decimal | None, Decimal | None, Decimal | None, str]],
    delay_seconds: float,
) -> tuple[Decimal | None, Decimal | None, Decimal | None, str]:
    query = ", ".join(
        value
        for value in [location["cidade"], location["estado"], location["pais"]]
        if value
    )
    if query in cache:
        return cache[query]

    local_key = (location["cidade"], location["estado"], location["pais"])
    if local_key in LOCAL_COORDINATES:
        latitude, longitude = LOCAL_COORDINATES[local_key]
        result = (latitude, longitude, Decimal("1"), "local")
        cache[query] = result
        return result

    if not user_agent:
        result = (None, None, Decimal("0"), "local")
        cache[query] = result
        return result

    response = requests.get(
        NOMINATIM_URL,
        params={"q": query, "format": "jsonv2", "limit": 1},
        headers={"User-Agent": user_agent},
        timeout=30,
    )
    response.raise_for_status()
    time.sleep(delay_seconds)
    data = response.json()
    if not data:
        result = (None, None, Decimal("0"), "nominatim")
    else:
        item = data[0]
        result = (
            Decimal(str(item["lat"])),
            Decimal(str(item["lon"])),
            Decimal(str(item.get("importance", 0))),
            "nominatim",
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
    source: str,
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
                source,
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
