from collections.abc import Sequence
from datetime import date

from app.backend.db import get_cursor
from app.backend.schemas import FilterParams
from app.backend.schemas import RankingDimension


RANKING_COLUMNS: dict[RankingDimension, str] = {
    "beneficiarios": "beneficiario_nome",
    "orgaos": "orgao_nome",
    "cargos": "cargo_descricao",
    "ugs": "unidade_gestora_nome",
}


def get_filter_options() -> dict:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT orgao_codigo_siafi AS value,
                   CONCAT(orgao_codigo_siafi, ' - ', orgao_nome) AS label
              FROM viagens
             WHERE orgao_codigo_siafi IS NOT NULL
             ORDER BY label
            """
        )
        orgaos = cursor.fetchall()

        cursor.execute(
            """
            SELECT DISTINCT beneficiario_nome AS value, beneficiario_nome AS label
              FROM viagens
             WHERE beneficiario_nome IS NOT NULL
             ORDER BY beneficiario_nome
             LIMIT 500
            """
        )
        beneficiarios = cursor.fetchall()

        cursor.execute(
            """
            SELECT DISTINCT cargo_descricao AS value, cargo_descricao AS label
              FROM viagens
             WHERE cargo_descricao IS NOT NULL
             ORDER BY cargo_descricao
             LIMIT 500
            """
        )
        cargos = cursor.fetchall()

        cursor.execute(
            """
            SELECT DISTINCT tipo_viagem AS value, tipo_viagem AS label
              FROM viagens
             WHERE tipo_viagem IS NOT NULL
             ORDER BY tipo_viagem
            """
        )
        tipos_viagem = cursor.fetchall()

    return {
        "orgaos": orgaos,
        "beneficiarios": beneficiarios,
        "cargos": cargos,
        "tipos_viagem": tipos_viagem,
    }


def get_kpis(filters: FilterParams) -> dict:
    where_sql, params = _build_where(filters)
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT COALESCE(SUM(valor_total_viagem), 0) AS valor_total,
                   COALESCE(SUM(valor_total_diarias), 0) AS valor_diarias,
                   COALESCE(SUM(valor_total_passagem), 0) AS valor_passagens,
                   COUNT(*) AS numero_viagens,
                   COALESCE(AVG(valor_total_viagem), 0) AS ticket_medio
              FROM viagens
             {where_sql}
            """,
            params,
        )
        return cursor.fetchone()


def get_ranking(
    dimension: RankingDimension,
    filters: FilterParams,
    limit: int = 20,
) -> list[dict]:
    column = RANKING_COLUMNS[dimension]
    where_sql, params = _build_where(filters)
    params.append(limit)

    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT COALESCE({column}, 'Nao informado') AS nome,
                   COUNT(*) AS quantidade,
                   COALESCE(SUM(valor_total_viagem), 0) AS valor_total
              FROM viagens
             {where_sql}
             GROUP BY COALESCE({column}, 'Nao informado')
             ORDER BY valor_total DESC
             LIMIT %s
            """,
            params,
        )
        return cursor.fetchall()


def get_time_series(filters: FilterParams) -> list[dict]:
    where_sql, params = _build_where(filters)
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT date_trunc('month', data_inicio_afastamento)::date AS periodo,
                   COUNT(*) AS quantidade,
                   COALESCE(SUM(valor_total_viagem), 0) AS valor_total
              FROM viagens
             {where_sql}
             GROUP BY date_trunc('month', data_inicio_afastamento)::date
             ORDER BY periodo
            """,
            params,
        )
        return cursor.fetchall()


def get_map_points(filters: FilterParams) -> list[dict]:
    where_sql, params = _build_where(filters, table_alias="v")
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT l.cidade,
                   l.estado,
                   l.pais,
                   l.latitude::float AS latitude,
                   l.longitude::float AS longitude,
                   COUNT(*) AS quantidade,
                   COALESCE(SUM(v.valor_total_viagem), 0) AS valor_total,
                   AVG(l.confidence)::float AS confidence
              FROM viagem_localidades l
              JOIN viagens v ON v.id = l.viagem_id
             {where_sql}
               AND l.latitude IS NOT NULL
               AND l.longitude IS NOT NULL
             GROUP BY l.cidade, l.estado, l.pais, l.latitude, l.longitude
             ORDER BY quantidade DESC
             LIMIT 500
            """,
            params,
        )
        return cursor.fetchall()


def _build_where(
    filters: FilterParams,
    table_alias: str | None = None,
) -> tuple[str, list]:
    prefix = f"{table_alias}." if table_alias else ""
    clauses = ["1 = 1"]
    params: list[Sequence[str] | str | date] = []

    if filters.orgao:
        clauses.append(f"{prefix}orgao_codigo_siafi = ANY(%s)")
        params.append(filters.orgao)
    if filters.beneficiario:
        clauses.append(f"{prefix}beneficiario_nome ILIKE %s")
        params.append(f"%{filters.beneficiario}%")
    if filters.cargo:
        clauses.append(f"{prefix}cargo_descricao ILIKE %s")
        params.append(f"%{filters.cargo}%")
    if filters.tipo_viagem:
        clauses.append(f"{prefix}tipo_viagem = %s")
        params.append(filters.tipo_viagem)
    if filters.data_inicio:
        clauses.append(f"{prefix}data_inicio_afastamento >= %s")
        params.append(filters.data_inicio)
    if filters.data_fim:
        clauses.append(f"{prefix}data_inicio_afastamento <= %s")
        params.append(filters.data_fim)

    return "WHERE " + " AND ".join(clauses), params
