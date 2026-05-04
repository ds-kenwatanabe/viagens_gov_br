import unittest
from unittest.mock import Mock

from src.api_client import ViagensAPIClient


class ViagensAPIClientTest(unittest.TestCase):
    def test_fetch_page_uses_page_copy_without_mutating_params(self):
        response = Mock()
        response.status_code = 200
        response.headers = {}
        response.json.return_value = []

        session = Mock()
        session.get.return_value = response

        params = {
            "dataIdaDe": "01/01/2023",
            "pagina": "1",
        }
        client = ViagensAPIClient(
            url="https://example.test/viagens",
            headers={"chave-api-dados": "token"},
            session=session,
        )

        client.fetch_page(params, page=3)

        self.assertEqual(params["pagina"], "1")
        session.get.assert_called_once_with(
            url="https://example.test/viagens",
            params={
                "dataIdaDe": "01/01/2023",
                "pagina": "3",
            },
            headers={"chave-api-dados": "token"},
            timeout=30,
        )

    def test_fetch_page_rejects_invalid_page(self):
        client = ViagensAPIClient(
            url="https://example.test/viagens",
            headers={"chave-api-dados": "token"},
            session=Mock(),
        )

        with self.assertRaises(ValueError):
            client.fetch_page({}, page=0)

    def test_fetch_page_retries_server_error_with_backoff(self):
        error_response = Mock()
        error_response.status_code = 500
        error_response.headers = {}

        success_response = Mock()
        success_response.status_code = 200
        success_response.headers = {}
        success_response.json.return_value = [{"id": 1}]

        session = Mock()
        session.get.side_effect = [error_response, success_response]
        sleep_func = Mock()

        client = ViagensAPIClient(
            url="https://example.test/viagens",
            headers={"chave-api-dados": "token"},
            backoff_seconds=2.0,
            session=session,
            sleep_func=sleep_func,
        )

        data = client.fetch_page({"pagina": "1"}, page=1)

        self.assertEqual(data, [{"id": 1}])
        self.assertEqual(session.get.call_count, 2)
        sleep_func.assert_called_once_with(2.0)

    def test_fetch_page_honors_retry_after_for_rate_limit(self):
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "5"}

        success_response = Mock()
        success_response.status_code = 200
        success_response.headers = {}
        success_response.json.return_value = []

        session = Mock()
        session.get.side_effect = [rate_limit_response, success_response]
        sleep_func = Mock()

        client = ViagensAPIClient(
            url="https://example.test/viagens",
            headers={"chave-api-dados": "token"},
            session=session,
            sleep_func=sleep_func,
        )

        client.fetch_page({"pagina": "1"}, page=1)

        self.assertEqual(session.get.call_count, 2)
        sleep_func.assert_called_once_with(5.0)


if __name__ == "__main__":
    unittest.main()
