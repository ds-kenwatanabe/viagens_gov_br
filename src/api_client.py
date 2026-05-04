from collections.abc import Callable
from collections.abc import Mapping
import logging
import time

import requests


RETRY_STATUS_CODES = {429, 500, 502, 503}
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class ViagensAPIClient:
    def __init__(
        self,
        url: str,
        headers: Mapping[str, str],
        timeout: float = 30,
        max_retries: int = 3,
        backoff_seconds: float = 2.0,
        session: requests.Session | None = None,
        sleep_func: Callable[[float], None] = time.sleep,
    ) -> None:
        self.url = url
        self.headers = dict(headers)
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.session = session or requests.Session()
        self.sleep_func = sleep_func

    def fetch_page(self, params: Mapping[str, str], page: int) -> list[dict]:
        if page < 1:
            raise ValueError("Page must be greater than or equal to 1")

        page_params = dict(params)
        page_params["pagina"] = str(page)

        response = self._get_with_retry(page_params)
        response.raise_for_status()

        data = response.json()
        if not isinstance(data, list):
            raise ValueError("Unexpected API response: expected a list of trips")

        return data

    def _get_with_retry(self, params: Mapping[str, str]) -> requests.Response:
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(
                    url=self.url,
                    params=dict(params),
                    headers=self.headers,
                    timeout=self.timeout,
                )
            except requests.RequestException:
                if attempt >= self.max_retries:
                    raise

                delay = self._backoff_delay(attempt)
                LOGGER.warning(
                    "Request failed before response. Retrying in %.1fs. Attempt %s/%s.",
                    delay,
                    attempt + 1,
                    self.max_retries,
                )
                self.sleep_func(delay)
                continue

            if response.status_code not in RETRY_STATUS_CODES:
                return response

            if attempt >= self.max_retries:
                return response

            delay = self._retry_delay(response, attempt)
            LOGGER.warning(
                "API returned HTTP %s. Retrying in %.1fs. Attempt %s/%s.",
                response.status_code,
                delay,
                attempt + 1,
                self.max_retries,
            )
            self.sleep_func(delay)

        raise RuntimeError("Unexpected retry loop termination")

    def _retry_delay(self, response: requests.Response, attempt: int) -> float:
        retry_after = response.headers.get("Retry-After")
        if response.status_code == 429 and retry_after:
            try:
                return max(float(retry_after), 0.0)
            except ValueError:
                LOGGER.warning("Ignoring invalid Retry-After header: %s", retry_after)

        return self._backoff_delay(attempt)

    def _backoff_delay(self, attempt: int) -> float:
        return self.backoff_seconds * (2**attempt)
