from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extensions import connection

from src.config import Settings


SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect_db(settings: Settings) -> connection:
    return psycopg2.connect(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
    )


def ensure_schema(conn: connection) -> None:
    with conn.cursor() as cursor:
        cursor.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()


def viagem_exists(conn: connection, viagem_id: int) -> bool:
    with conn.cursor() as cursor:
        cursor.execute("SELECT EXISTS(SELECT 1 FROM viagens WHERE id = %s)", (viagem_id,))
        return bool(cursor.fetchone()[0])


def insert_viagem(conn: connection, item: dict[str, Any]) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO viagens (
                id,
                motivo,
                pcdp,
                ano,
                num_pcdp,
                justificativa_urgente,
                urgencia_viagem,
                situacao,
                beneficiario_cpf,
                beneficiario_nis,
                beneficiario_nome,
                cargo_codigo_siape,
                cargo_descricao,
                funcao_codigo_siape,
                funcao_descricao,
                tipo_viagem,
                orgao_nome,
                orgao_codigo_siafi,
                orgao_cnpj,
                orgao_sigla,
                orgao_descricao_poder,
                orgao_pagamento_nome,
                orgao_pagamento_codigo_siafi,
                orgao_pagamento_cnpj,
                orgao_pagamento_sigla,
                unidade_gestora_codigo,
                unidade_gestora_nome,
                unidade_gestora_descricao_poder,
                data_inicio_afastamento,
                data_fim_afastamento,
                valor_total_restituicao,
                valor_total_taxa_agenciamento,
                valor_multa,
                valor_total_diarias,
                valor_total_passagem,
                valor_total_viagem,
                valor_total_devolucao
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            )
            """,
            _viagem_values(item),
        )


def _viagem_values(item: dict[str, Any]) -> tuple[Any, ...]:
    viagem = item.get("viagem") or {}
    beneficiario = item.get("beneficiario") or {}
    cargo = item.get("cargo") or {}
    funcao = item.get("funcao") or {}
    orgao = item.get("orgao") or {}
    orgao_pagamento = item.get("orgaoPagamento") or {}
    unidade_gestora = item.get("unidadeGestoraResponsavel") or {}

    return (
        item.get("id"),
        viagem.get("motivo"),
        viagem.get("pcdp"),
        viagem.get("ano"),
        viagem.get("numPcdp"),
        viagem.get("justificativaUrgente"),
        viagem.get("urgenciaViagem"),
        item.get("situacao"),
        beneficiario.get("cpfFormatado"),
        beneficiario.get("nis"),
        beneficiario.get("nome"),
        cargo.get("codigoSIAPE"),
        cargo.get("descricao"),
        funcao.get("codigoSIAPE"),
        funcao.get("descricao"),
        item.get("tipoViagem"),
        orgao.get("nome"),
        orgao.get("codigoSIAFI"),
        orgao.get("cnpj"),
        orgao.get("sigla"),
        orgao.get("descricaoPoder"),
        orgao_pagamento.get("nome"),
        orgao_pagamento.get("codigoSIAFI"),
        orgao_pagamento.get("cnpj"),
        orgao_pagamento.get("sigla"),
        unidade_gestora.get("codigo"),
        unidade_gestora.get("nome"),
        unidade_gestora.get("descricaoPoder"),
        item.get("dataInicioAfastamento"),
        item.get("dataFimAfastamento"),
        item.get("valorTotalRestituicao"),
        item.get("valorTotalTaxaAgenciamento"),
        item.get("valorMulta"),
        item.get("valorTotalDiarias"),
        item.get("valorTotalPassagem"),
        item.get("valorTotalViagem"),
        item.get("valorTotalDevolucao"),
    )
