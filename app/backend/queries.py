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


def get_org_comparison(filters: FilterParams) -> list[dict]:
    where_sql, params = _build_where(filters)
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT COALESCE(orgao_nome, 'Nao informado') AS nome,
                   COUNT(*) AS quantidade,
                   COALESCE(SUM(valor_total_viagem), 0) AS valor_total
              FROM vw_viagens_dashboard
             {where_sql}
             GROUP BY COALESCE(orgao_nome, 'Nao informado')
             ORDER BY valor_total DESC
             LIMIT 30
            """,
            params,
        )
        return cursor.fetchall()


def get_ranking(
    dimension: RankingDimension,
    filters: FilterParams,
    limit: int = 20,
    order_by: str = "valor",
) -> list[dict]:
    column = RANKING_COLUMNS[dimension]
    where_sql, params = _build_where(filters)
    params.append(limit)

    with get_cursor() as cursor:
        order_sql = "quantidade DESC, valor_total DESC" if order_by == "quantidade" else "valor_total DESC"
        cursor.execute(
            f"""
            SELECT COALESCE({column}, 'Nao informado') AS nome,
                   COUNT(*) AS quantidade,
                   COALESCE(SUM(valor_total_viagem), 0) AS valor_total
              FROM viagens
             {where_sql}
             GROUP BY COALESCE({column}, 'Nao informado')
             ORDER BY {order_sql}
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
    where_sql, params = _build_where(filters)
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT id,
                   orgao_nome,
                   beneficiario_nome,
                   motivo,
                   tipo_viagem,
                   data_inicio_afastamento,
                   data_fim_afastamento,
                   cidade,
                   estado,
                   pais,
                   latitude::float AS latitude,
                   longitude::float AS longitude,
                   1 AS quantidade,
                   COALESCE(valor_total_viagem, 0) AS valor_total,
                   confidence::float AS confidence
              FROM vw_mapa_viagens
             {where_sql}
             ORDER BY valor_total_viagem DESC NULLS LAST
             LIMIT 500
            """,
            params,
        )
        return cursor.fetchall()


def get_trip_details(filters: FilterParams, limit: int = 100) -> list[dict]:
    where_sql, params = _build_where(filters)
    params.append(limit)
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT id,
                   orgao_nome,
                   beneficiario_nome,
                   cargo_descricao,
                   tipo_viagem,
                   motivo,
                   data_inicio_afastamento,
                   data_fim_afastamento,
                   COALESCE(valor_total_viagem, 0) AS valor_total_viagem,
                   COALESCE(valor_total_diarias, 0) AS valor_total_diarias,
                   COALESCE(valor_total_passagem, 0) AS valor_total_passagem
              FROM vw_viagens_dashboard
             {where_sql}
             ORDER BY valor_total_viagem DESC NULLS LAST
             LIMIT %s
            """,
            params,
        )
        return cursor.fetchall()


def get_cargo_distribution(filters: FilterParams, limit: int = 30) -> list[dict]:
    where_sql, params = _build_where(filters)
    params.append(limit)
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT COALESCE(cargo_descricao, 'Nao informado') AS nome,
                   COUNT(*) AS quantidade,
                   COALESCE(AVG(valor_total_viagem), 0) AS valor_medio
              FROM vw_viagens_dashboard
             {where_sql}
             GROUP BY COALESCE(cargo_descricao, 'Nao informado')
             ORDER BY quantidade DESC
             LIMIT %s
            """,
            params,
        )
        return cursor.fetchall()


def get_outliers(filters: FilterParams, kind: str, limit: int = 30) -> list[dict]:
    where_sql, params = _build_where(filters)
    params.append(limit)
    query = _outlier_query(kind, where_sql)
    with get_cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


def _outlier_query(kind: str, where_sql: str) -> str:
    if kind == "valores_altos":
        return f"""
            SELECT CONCAT(id, ' - ', COALESCE(beneficiario_nome, 'Nao informado')) AS nome,
                   1 AS quantidade,
                   COALESCE(valor_total_viagem, 0) AS valor_total,
                   COALESCE(valor_total_viagem, 0) AS valor_medio,
                   COALESCE(motivo, '') AS detalhe
              FROM vw_viagens_dashboard
             {where_sql}
             ORDER BY valor_total_viagem DESC NULLS LAST
             LIMIT %s
        """
    if kind == "recorrentes":
        return f"""
            SELECT COALESCE(beneficiario_nome, 'Nao informado') AS nome,
                   COUNT(*) AS quantidade,
                   COALESCE(SUM(valor_total_viagem), 0) AS valor_total,
                   COALESCE(AVG(valor_total_viagem), 0) AS valor_medio,
                   MIN(data_inicio_afastamento)::text || ' a ' || MAX(data_inicio_afastamento)::text AS detalhe
              FROM vw_viagens_dashboard
             {where_sql}
             GROUP BY COALESCE(beneficiario_nome, 'Nao informado')
            HAVING COUNT(*) >= 5
             ORDER BY quantidade DESC, valor_total DESC
             LIMIT %s
        """
    if kind == "cargos_media":
        return f"""
            SELECT COALESCE(cargo_descricao, 'Nao informado') AS nome,
                   COUNT(*) AS quantidade,
                   COALESCE(SUM(valor_total_viagem), 0) AS valor_total,
                   COALESCE(AVG(valor_total_viagem), 0) AS valor_medio,
                   NULL AS detalhe
              FROM vw_viagens_dashboard
             {where_sql}
             GROUP BY COALESCE(cargo_descricao, 'Nao informado')
            HAVING COUNT(*) >= 5
             ORDER BY valor_medio DESC
             LIMIT %s
        """

    return f"""
        SELECT COALESCE(beneficiario_nome, 'Nao informado') AS nome,
               COUNT(*) AS quantidade,
               COALESCE(SUM(valor_total_viagem), 0) AS valor_total,
               COALESCE(AVG(valor_total_viagem), 0) AS valor_medio,
               'Viagens de ate 2 dias' AS detalhe
          FROM vw_viagens_dashboard
         {where_sql}
           AND data_inicio_afastamento IS NOT NULL
           AND data_fim_afastamento IS NOT NULL
           AND data_fim_afastamento - data_inicio_afastamento <= 2
         GROUP BY COALESCE(beneficiario_nome, 'Nao informado')
        HAVING COUNT(*) >= 3
         ORDER BY quantidade DESC, valor_total DESC
         LIMIT %s
    """


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
