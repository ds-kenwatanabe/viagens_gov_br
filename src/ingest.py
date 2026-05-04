from collections.abc import Mapping
from contextlib import closing

from requests import HTTPError

from src.api_client import ViagensAPIClient
from src.config import API_URL, DEFAULT_PARAMS, build_headers, load_settings
from src.database import connect_db, ensure_schema, insert_viagem, viagem_exists


def ingest_viagens(
    params: Mapping[str, str] | None = None,
    max_requests: int = 100_000,
) -> int:
    settings = load_settings()
    headers = build_headers(settings.api_key)
    client = ViagensAPIClient(API_URL, headers)
    request_params = dict(params or DEFAULT_PARAMS)

    inserted_rows = 0
    page = 1

    with closing(connect_db(settings)) as conn:
        ensure_schema(conn)

        while max_requests > 0:
            try:
                data = client.fetch_page(request_params, page)
            except HTTPError as exc:
                print(f"A solicitacao para a pagina {page} falhou: {exc}")
                break

            if not data:
                print("A pagina nao retornou dados. Encerrando a consulta.")
                break

            for item in data:
                viagem_id = item.get("id")
                if viagem_id is None:
                    print(f"Registro sem id ignorado: {item}")
                    continue

                if not viagem_exists(conn, viagem_id):
                    insert_viagem(conn, item)
                    inserted_rows += 1

                max_requests -= 1
                if max_requests == 0:
                    print("Numero maximo de requisicoes da API atingido.")
                    break

            conn.commit()
            page += 1

    print(
        "Dados das viagens foram processados com sucesso. "
        f"Paginas consultadas: {page - 1}. Registros inseridos: {inserted_rows}."
    )
    return inserted_rows
