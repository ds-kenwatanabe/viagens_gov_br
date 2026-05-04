import os
from dataclasses import dataclass

from dotenv import load_dotenv


API_URL = "https://api.portaldatransparencia.gov.br/api-de-dados/viagens"

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
    )


def build_headers(api_key: str) -> dict[str, str]:
    return {
        "accept": "*/*",
        "chave-api-dados": api_key,
    }
