import re
import unicodedata


KNOWN_LOCATIONS = {
    "brasilia": ("Brasilia", "DF", "Brasil"),
    "sao paulo": ("Sao Paulo", "SP", "Brasil"),
    "rio de janeiro": ("Rio de Janeiro", "RJ", "Brasil"),
    "manaus": ("Manaus", "AM", "Brasil"),
    "recife": ("Recife", "PE", "Brasil"),
    "salvador": ("Salvador", "BA", "Brasil"),
    "fortaleza": ("Fortaleza", "CE", "Brasil"),
    "belem": ("Belem", "PA", "Brasil"),
    "curitiba": ("Curitiba", "PR", "Brasil"),
    "porto alegre": ("Porto Alegre", "RS", "Brasil"),
    "lisboa": ("Lisboa", None, "Portugal"),
    "washington": ("Washington", "DC", "Estados Unidos"),
    "nova york": ("Nova York", "NY", "Estados Unidos"),
    "paris": ("Paris", None, "Franca"),
    "londres": ("Londres", None, "Reino Unido"),
    "roma": ("Roma", None, "Italia"),
    "madrid": ("Madrid", None, "Espanha"),
    "buenos aires": ("Buenos Aires", None, "Argentina"),
    "montevideu": ("Montevideu", None, "Uruguai"),
    "santiago": ("Santiago", None, "Chile"),
}

UF_PATTERN = re.compile(r"\b([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç\s.'-]+?)/(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b")


def extract_locations(text: str | None) -> list[dict[str, str | None]]:
    if not text:
        return []

    locations: list[dict[str, str | None]] = []
    seen: set[str] = set()

    for match in UF_PATTERN.finditer(text):
        city = _clean_city(match.group(1))
        state = match.group(2)
        key = _normalize(f"{city}/{state}")
        if key not in seen:
            seen.add(key)
            locations.append(
                {
                    "local_texto": f"{city}/{state}",
                    "cidade": city,
                    "estado": state,
                    "pais": "Brasil",
                }
            )

    normalized_text = _normalize(text)
    for key, (city, state, country) in KNOWN_LOCATIONS.items():
        if key in normalized_text and key not in seen:
            seen.add(key)
            locations.append(
                {
                    "local_texto": city,
                    "cidade": city,
                    "estado": state,
                    "pais": country,
                }
            )

    return locations


def _clean_city(value: str) -> str:
    clean_value = " ".join(value.strip(" -.,;:").split())
    for separator in (" em ", " para ", " de ", " da ", " do "):
        if separator in clean_value.lower():
            clean_value = clean_value.split(separator.strip(), maxsplit=1)[-1].strip()
    return clean_value


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_value.lower()
