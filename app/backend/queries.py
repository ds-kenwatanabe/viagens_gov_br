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
            SELECT beneficiario_nome AS value,
                   beneficiario_nome || ' (' || COUNT(*)::text || ')' AS label
              FROM viagens
             WHERE beneficiario_nome IS NOT NULL
               AND beneficiario_nome <> ''
             GROUP BY beneficiario_nome
             ORDER BY COUNT(*) DESC, beneficiario_nome
             LIMIT 500
            """
        )
        beneficiarios = cursor.fetchall()

        cursor.execute(
            """
            SELECT cargo_descricao AS value,
                   cargo_descricao || ' (' || COUNT(*)::text || ')' AS label
              FROM viagens
             WHERE cargo_descricao IS NOT NULL
               AND cargo_descricao <> ''
             GROUP BY cargo_descricao
             ORDER BY COUNT(*) DESC, cargo_descricao
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


def search_filter_options(kind: str, search: str = "", limit: int = 80) -> list[dict]:
    columns = {
        "beneficiarios": "beneficiario_nome",
        "cargos": "cargo_descricao",
    }
    column = columns[kind]
    params: list[str | int] = []
    search_sql = ""
    if search:
        search_sql = f"AND {column} ILIKE %s"
        params.append(f"%{search}%")
    params.append(limit)

    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT {column} AS value,
                   {column} || ' (' || COUNT(*)::text || ')' AS label
              FROM viagens
             WHERE {column} IS NOT NULL
               AND {column} <> ''
               {search_sql}
             GROUP BY {column}
             ORDER BY COUNT(*) DESC, {column}
             LIMIT %s
            """,
            params,
        )
        return cursor.fetchall()


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
            SELECT COALESCE(orgao_nome, 'Não informado') AS nome,
                   COUNT(*) AS quantidade,
                   COALESCE(SUM(valor_total_viagem), 0) AS valor_total
              FROM vw_viagens_dashboard
             {where_sql}
             GROUP BY COALESCE(orgao_nome, 'Não informado')
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
            SELECT COALESCE({column}, 'Não informado') AS nome,
                   COUNT(*) AS quantidade,
                   COALESCE(SUM(valor_total_viagem), 0) AS valor_total
              FROM viagens
             {where_sql}
             GROUP BY COALESCE({column}, 'Não informado')
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


def get_map_points(
    filters: FilterParams,
    map_mode: str = "points",
    limit: int = 500,
) -> list[dict]:
    if map_mode == "clusters":
        return get_map_clusters(filters, limit)

    where_sql, params = _build_where(filters)
    params.append(limit)
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
             LIMIT %s
            """,
            params,
        )
        return cursor.fetchall()


def get_map_clusters(filters: FilterParams, limit: int = 2000) -> list[dict]:
    where_sql, params = _build_where(filters)
    params.append(limit)
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT NULL::integer AS id,
                   CASE
                       WHEN COUNT(DISTINCT orgao_nome) = 1 THEN MAX(orgao_nome)
                       ELSE 'Múltiplos órgãos'
                   END AS orgao_nome,
                   NULL::text AS beneficiario_nome,
                   NULL::text AS motivo,
                   CASE
                       WHEN COUNT(DISTINCT tipo_viagem) = 1 THEN MAX(tipo_viagem)
                       ELSE 'Misto'
                   END AS tipo_viagem,
                   MIN(data_inicio_afastamento) AS data_inicio_afastamento,
                   MAX(data_fim_afastamento) AS data_fim_afastamento,
                   cidade,
                   estado,
                   pais,
                   latitude::float AS latitude,
                   longitude::float AS longitude,
                   COUNT(*) AS quantidade,
                   COALESCE(SUM(valor_total_viagem), 0) AS valor_total,
                   AVG(confidence)::float AS confidence
              FROM vw_mapa_viagens
             {where_sql}
             GROUP BY cidade, estado, pais, latitude, longitude
             ORDER BY quantidade DESC, valor_total DESC
             LIMIT %s
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
            SELECT COALESCE(cargo_descricao, 'Não informado') AS nome,
                   COUNT(*) AS quantidade,
                   COALESCE(AVG(valor_total_viagem), 0) AS valor_medio
              FROM vw_viagens_dashboard
             {where_sql}
             GROUP BY COALESCE(cargo_descricao, 'Não informado')
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


def get_quality_report(filters: FilterParams, limit: int = 20) -> dict:
    where_sql, params = _build_where(filters, "v")
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            WITH base AS (
                SELECT v.id, v.motivo
                  FROM viagens v
                 {where_sql}
            ),
            local_stats AS (
                SELECT l.viagem_id,
                       BOOL_OR(
                           COALESCE(NULLIF(l.fonte, ''), 'none') <> 'none'
                           AND COALESCE(l.local_texto, '') <> '__NO_LOCATION__'
                       ) AS local_extraido,
                       BOOL_OR(l.latitude IS NOT NULL AND l.longitude IS NOT NULL) AS geocodificada
                  FROM viagem_localidades l
                  JOIN base b ON b.id = l.viagem_id
                 GROUP BY l.viagem_id
            ),
            confidence_stats AS (
                SELECT AVG(l.confidence)::float AS confianca_media
                  FROM viagem_localidades l
                  JOIN base b ON b.id = l.viagem_id
                 WHERE l.latitude IS NOT NULL
                   AND l.longitude IS NOT NULL
            )
            SELECT COUNT(*) AS total_viagens,
                   COUNT(*) FILTER (
                       WHERE motivo IS NULL OR btrim(motivo) = ''
                   ) AS motivo_vazio,
                   COUNT(*) FILTER (
                       WHERE NOT COALESCE(local_stats.local_extraido, false)
                   ) AS sem_local_extraido,
                   COUNT(*) FILTER (
                       WHERE COALESCE(local_stats.geocodificada, false)
                   ) AS geocodificadas,
                   MAX(confidence_stats.confianca_media) AS confianca_media
              FROM base
              LEFT JOIN local_stats ON local_stats.viagem_id = base.id
              CROSS JOIN confidence_stats
            """,
            params,
        )
        summary = cursor.fetchone()

        cursor.execute(
            f"""
            WITH base AS (
                SELECT v.id
                  FROM viagens v
                 {where_sql}
            ),
            source_counts AS (
                SELECT CASE
                           WHEN LOWER(COALESCE(NULLIF(l.fonte, ''), 'none')) IN ('local', 'nominatim')
                               THEN LOWER(COALESCE(NULLIF(l.fonte, ''), 'none'))
                           ELSE 'none'
                       END AS fonte,
                       COUNT(*) AS quantidade
                  FROM viagem_localidades l
                  JOIN base b ON b.id = l.viagem_id
                 GROUP BY 1
            ),
            expected_sources AS (
                SELECT unnest(ARRAY['local', 'nominatim', 'none']) AS fonte
            )
            SELECT expected_sources.fonte,
                   COALESCE(source_counts.quantidade, 0) AS quantidade
              FROM expected_sources
              LEFT JOIN source_counts ON source_counts.fonte = expected_sources.fonte
             ORDER BY CASE expected_sources.fonte
                          WHEN 'local' THEN 1
                          WHEN 'nominatim' THEN 2
                          ELSE 3
                      END
            """,
            params,
        )
        fontes = cursor.fetchall()

        motivo_params = [*params, limit]
        cursor.execute(
            f"""
            WITH base AS (
                SELECT v.id, v.motivo, v.valor_total_viagem
                  FROM viagens v
                 {where_sql}
            ),
            local_stats AS (
                SELECT l.viagem_id,
                       BOOL_OR(
                           COALESCE(NULLIF(l.fonte, ''), 'none') <> 'none'
                           AND COALESCE(l.local_texto, '') <> '__NO_LOCATION__'
                       ) AS local_extraido
                  FROM viagem_localidades l
                  JOIN base b ON b.id = l.viagem_id
                 GROUP BY l.viagem_id
            )
            SELECT COALESCE(NULLIF(btrim(base.motivo), ''), 'NÃ£o informado') AS nome,
                   COUNT(*) AS quantidade,
                   COALESCE(SUM(base.valor_total_viagem), 0) AS valor_total
              FROM base
              LEFT JOIN local_stats ON local_stats.viagem_id = base.id
             WHERE NOT COALESCE(local_stats.local_extraido, false)
               AND base.motivo IS NOT NULL
               AND btrim(base.motivo) <> ''
             GROUP BY COALESCE(NULLIF(btrim(base.motivo), ''), 'NÃ£o informado')
             ORDER BY quantidade DESC, valor_total DESC
             LIMIT %s
            """,
            motivo_params,
        )
        motivos_sem_local = cursor.fetchall()

    return {
        "summary": summary,
        "fontes": fontes,
        "motivos_sem_local": motivos_sem_local,
    }


def _outlier_query(kind: str, where_sql: str) -> str:
    if kind == "valores_altos":
        return f"""
            SELECT CONCAT(id, ' - ', COALESCE(beneficiario_nome, 'Não informado')) AS nome,
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
            SELECT COALESCE(beneficiario_nome, 'Não informado') AS nome,
                   COUNT(*) AS quantidade,
                   COALESCE(SUM(valor_total_viagem), 0) AS valor_total,
                   COALESCE(AVG(valor_total_viagem), 0) AS valor_medio,
                   MIN(data_inicio_afastamento)::text || ' a ' || MAX(data_inicio_afastamento)::text AS detalhe
              FROM vw_viagens_dashboard
             {where_sql}
             GROUP BY COALESCE(beneficiario_nome, 'Não informado')
            HAVING COUNT(*) >= 5
             ORDER BY quantidade DESC, valor_total DESC
             LIMIT %s
        """
    if kind == "cargos_media":
        return f"""
            SELECT COALESCE(cargo_descricao, 'Não informado') AS nome,
                   COUNT(*) AS quantidade,
                   COALESCE(SUM(valor_total_viagem), 0) AS valor_total,
                   COALESCE(AVG(valor_total_viagem), 0) AS valor_medio,
                   NULL AS detalhe
              FROM vw_viagens_dashboard
             {where_sql}
             GROUP BY COALESCE(cargo_descricao, 'Não informado')
            HAVING COUNT(*) >= 5
             ORDER BY valor_medio DESC
             LIMIT %s
        """

    return f"""
        SELECT COALESCE(beneficiario_nome, 'Não informado') AS nome,
               COUNT(*) AS quantidade,
               COALESCE(SUM(valor_total_viagem), 0) AS valor_total,
               COALESCE(AVG(valor_total_viagem), 0) AS valor_medio,
               'Viagens de até 2 dias' AS detalhe
          FROM vw_viagens_dashboard
         {where_sql}
           AND data_inicio_afastamento IS NOT NULL
           AND data_fim_afastamento IS NOT NULL
           AND data_fim_afastamento - data_inicio_afastamento <= 2
         GROUP BY COALESCE(beneficiario_nome, 'Não informado')
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
    if filters.motivo_contem:
        clauses.append(f"{prefix}motivo ILIKE %s")
        params.append(f"%{filters.motivo_contem}%")
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
