from collections.abc import Mapping

import requests


class ViagensAPIClient:
    def __init__(
        self,
        url: str,
        headers: Mapping[str, str],
        timeout: int = 30,
        session: requests.Session | None = None,
    ) -> None:
        self.url = url
        self.headers = dict(headers)
        self.timeout = timeout
        self.session = session or requests.Session()

    def fetch_page(self, params: Mapping[str, str], page: int) -> list[dict]:
        if page < 1:
            raise ValueError("Page must be greater than or equal to 1")

        page_params = dict(params)
        page_params["pagina"] = str(page)

        response = self.session.get(
            url=self.url,
            params=page_params,
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        if not isinstance(data, list):
            raise ValueError("Unexpected API response: expected a list of trips")

        return data
