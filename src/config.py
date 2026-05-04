import os
from dataclasses import dataclass

from dotenv import load_dotenv


API_URL = "https://api.portaldatransparencia.gov.br/api-de-dados/viagens"
API_TIMEOUT_SECONDS = 30
API_MAX_RETRIES = 3
API_BACKOFF_SECONDS = 2.0
API_PAGE_DELAY_SECONDS = 1.0

DEFAULT_PARAMS = {
    "dataIdaDe": "01/01/2023",
    "dataIdaAte": "31/01/2023",
    "dataRetornoDe": "01/01/2023",
    "dataRetornoAte": "31/01/2023",
    "codigoOrgao": "20000",
    "pagina": "1",
}


@dataclass(frozen=True)
class Settings:
    api_key: str
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    api_timeout_seconds: float
    api_max_retries: int
    api_backoff_seconds: float
    api_page_delay_seconds: float


def load_settings() -> Settings:
    load_dotenv()

    required_vars = {
        "API_KEY": os.getenv("API_KEY"),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
    }
    missing_vars = [name for name, value in required_vars.items() if not value]

    if missing_vars:
        missing = ", ".join(missing_vars)
        raise RuntimeError(f"Missing required environment variables: {missing}")

    return Settings(
        api_key=required_vars["API_KEY"],
        db_name=required_vars["DB_NAME"],
        db_user=required_vars["DB_USER"],
        db_password=required_vars["DB_PASSWORD"],
        db_host=required_vars["DB_HOST"],
        db_port=required_vars["DB_PORT"],
        api_timeout_seconds=_get_float("API_TIMEOUT_SECONDS", API_TIMEOUT_SECONDS),
        api_max_retries=_get_int("API_MAX_RETRIES", API_MAX_RETRIES),
        api_backoff_seconds=_get_float("API_BACKOFF_SECONDS", API_BACKOFF_SECONDS),
        api_page_delay_seconds=_get_float(
            "API_PAGE_DELAY_SECONDS",
            API_PAGE_DELAY_SECONDS,
        ),
    )


def build_headers(api_key: str) -> dict[str, str]:
    return {
        "accept": "*/*",
        "chave-api-dados": api_key,
    }


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    return float(value)


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)
