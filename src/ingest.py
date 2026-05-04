import argparse
from collections.abc import Callable
from collections.abc import Mapping
from contextlib import closing
from datetime import date
from datetime import datetime
from datetime import timedelta
import logging
import sys
import time

from requests import RequestException

from src.api_client import ViagensAPIClient
from src.config import API_URL, DEFAULT_PARAMS, build_headers, load_settings
from src.database import connect_db, ensure_schema, insert_viagem


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def build_params(data_inicio: str, data_fim: str, orgao: str) -> dict[str, str]:
    if _parse_iso_date(data_fim) < _parse_iso_date(data_inicio):
        raise argparse.ArgumentTypeError(
            "Data final deve ser maior ou igual a data inicial."
        )

    data_inicio_api = _format_api_date(data_inicio)
    data_fim_api = _format_api_date(data_fim)

    return {
        "dataIdaDe": data_inicio_api,
        "dataIdaAte": data_fim_api,
        "dataRetornoDe": data_inicio_api,
        "dataRetornoAte": data_fim_api,
        "codigoOrgao": orgao,
        "pagina": "1",
    }


def build_monthly_windows(data_inicio: str, data_fim: str) -> list[tuple[str, str]]:
    start_date = _parse_iso_date(data_inicio).date()
    end_date = _parse_iso_date(data_fim).date()

    if end_date < start_date:
        raise argparse.ArgumentTypeError(
            "Data final deve ser maior ou igual a data inicial."
        )

    windows = []
    current_start = start_date
    while current_start <= end_date:
        current_end = min(_last_day_of_month(current_start), end_date)
        windows.append((current_start.isoformat(), current_end.isoformat()))
        current_start = current_end + timedelta(days=1)

    return windows


def parse_orgaos(orgao: str | None, orgaos: str | None) -> list[str]:
    selected_orgaos = []
    if orgao:
        selected_orgaos.append(orgao)
    if orgaos:
        selected_orgaos.extend(item.strip() for item in orgaos.split(",") if item.strip())

    if not selected_orgaos:
        raise argparse.ArgumentTypeError("Informe --orgao ou --orgaos.")

    return list(dict.fromkeys(selected_orgaos))


def ingest_viagens(
    params: Mapping[str, str] | None = None,
    max_requests: int = 100_000,
    sleep_func: Callable[[float], None] = time.sleep,
) -> int:
    settings = load_settings()
    headers = build_headers(settings.api_key)
    client = ViagensAPIClient(
        API_URL,
        headers,
        timeout=settings.api_timeout_seconds,
        max_retries=settings.api_max_retries,
        backoff_seconds=settings.api_backoff_seconds,
        sleep_func=sleep_func,
    )
    request_params = dict(params or DEFAULT_PARAMS)

    inserted_rows = 0
    page = 1
    codigo_orgao = request_params.get("codigoOrgao", "")
    periodo_ida = f"{request_params.get('dataIdaDe', '')}-{request_params.get('dataIdaAte', '')}"
    periodo_retorno = (
        f"{request_params.get('dataRetornoDe', '')}-{request_params.get('dataRetornoAte', '')}"
    )

    with closing(connect_db(settings)) as conn:
        ensure_schema(conn)

        while max_requests > 0:
            LOGGER.info(
                "Consultando pagina=%s orgao=%s periodo_ida=%s periodo_retorno=%s",
                page,
                codigo_orgao,
                periodo_ida,
                periodo_retorno,
            )

            try:
                data = client.fetch_page(request_params, page)
            except RequestException as exc:
                LOGGER.error(
                    "Falha ao consultar pagina=%s orgao=%s periodo_ida=%s periodo_retorno=%s: %s",
                    page,
                    codigo_orgao,
                    periodo_ida,
                    periodo_retorno,
                    exc,
                )
                break

            if not data:
                LOGGER.info(
                    "Pagina vazia. Encerrando consulta para orgao=%s periodo_ida=%s periodo_retorno=%s",
                    codigo_orgao,
                    periodo_ida,
                    periodo_retorno,
                )
                break

            page_inserted_rows = 0
            for item in data:
                viagem_id = item.get("id")
                if viagem_id is None:
                    LOGGER.warning("Registro sem id ignorado: %s", item)
                    continue

                if insert_viagem(conn, item):
                    inserted_rows += 1
                    page_inserted_rows += 1

                max_requests -= 1
                if max_requests == 0:
                    LOGGER.info("Numero maximo de requisicoes da API atingido.")
                    break

            conn.commit()
            LOGGER.info(
                "Pagina=%s processada. Registros recebidos=%s inseridos=%s orgao=%s",
                page,
                len(data),
                page_inserted_rows,
                codigo_orgao,
            )
            page += 1

            if max_requests > 0:
                sleep_func(settings.api_page_delay_seconds)

    LOGGER.info(
        "Dados das viagens foram processados com sucesso. "
        "Paginas consultadas=%s registros_inseridos=%s orgao=%s periodo_ida=%s periodo_retorno=%s",
        page - 1,
        inserted_rows,
        codigo_orgao,
        periodo_ida,
        periodo_retorno,
    )
    return inserted_rows


def ingest_windows(
    orgaos: list[str],
    windows: list[tuple[str, str]],
    max_requests: int = 100_000,
    sleep_func: Callable[[float], None] = time.sleep,
) -> int:
    total_inserted_rows = 0
    total_windows = len(orgaos) * len(windows)
    current_window = 1

    for orgao in orgaos:
        for data_inicio, data_fim in windows:
            LOGGER.info(
                "Iniciando janela %s/%s orgao=%s data_inicio=%s data_fim=%s",
                current_window,
                total_windows,
                orgao,
                data_inicio,
                data_fim,
            )
            params = build_params(data_inicio, data_fim, orgao)
            total_inserted_rows += ingest_viagens(
                params=params,
                max_requests=max_requests,
                sleep_func=sleep_func,
            )
            current_window += 1

    LOGGER.info("Lote finalizado. Total de registros inseridos=%s", total_inserted_rows)
    return total_inserted_rows


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        stream=sys.stdout,
    )
    orgaos = parse_orgaos(args.orgao, args.orgaos)
    windows = build_monthly_windows(args.data_inicio, args.data_fim)
    ingest_windows(orgaos=orgaos, windows=windows, max_requests=args.max_requests)
    return 0


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingere dados de viagens do Portal da Transparencia.",
    )
    parser.add_argument(
        "--data-inicio",
        required=True,
        type=_validate_iso_date,
        help="Data inicial no formato YYYY-MM-DD.",
    )
    parser.add_argument(
        "--data-fim",
        required=True,
        type=_validate_iso_date,
        help="Data final no formato YYYY-MM-DD.",
    )
    parser.add_argument(
        "--orgao",
        required=False,
        help="Codigo SIAFI do orgao consultado.",
    )
    parser.add_argument(
        "--orgaos",
        required=False,
        help="Codigos SIAFI separados por virgula para consulta em lote.",
    )
    parser.add_argument(
        "--max-requests",
        type=int,
        default=100_000,
        help="Quantidade maxima de registros processados nesta execucao.",
    )
    args = parser.parse_args(argv)
    try:
        parse_orgaos(args.orgao, args.orgaos)
        build_monthly_windows(args.data_inicio, args.data_fim)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    return args


def _validate_iso_date(value: str) -> str:
    _format_api_date(value)
    return value


def _format_api_date(value: str) -> str:
    return _parse_iso_date(value).strftime("%d/%m/%Y")


def _parse_iso_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Data invalida: {value}. Use o formato YYYY-MM-DD."
        ) from exc


def _last_day_of_month(value: date) -> date:
    if value.month == 12:
        next_month = date(value.year + 1, 1, 1)
    else:
        next_month = date(value.year, value.month + 1, 1)
    return next_month - timedelta(days=1)


if __name__ == "__main__":
    raise SystemExit(main())
