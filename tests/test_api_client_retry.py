import unittest
from unittest.mock import Mock

import requests

from src.api_client import ViagensAPIClient


class APIClientRetryTest(unittest.TestCase):
    def test_retries_request_exception_with_exponential_backoff(self):
        success_response = Mock()
        success_response.status_code = 200
        success_response.headers = {}
        success_response.json.return_value = [{"id": 1}]

        session = Mock()
        session.get.side_effect = [
            requests.Timeout("timeout"),
            requests.ConnectionError("connection"),
            success_response,
        ]
        sleep_func = Mock()

        client = ViagensAPIClient(
            url="https://example.test/viagens",
            headers={"chave-api-dados": "token"},
            backoff_seconds=1.5,
            max_retries=3,
            session=session,
            sleep_func=sleep_func,
        )

        data = client.fetch_page({}, page=2)

        self.assertEqual(data, [{"id": 1}])
        self.assertEqual(session.get.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep_func.call_args_list], [1.5, 3.0])

    def test_returns_final_retry_response_for_repeated_rate_limit(self):
        responses = []
        for _ in range(3):
            response = Mock()
            response.status_code = 429
            response.headers = {}
            responses.append(response)

        session = Mock()
        session.get.side_effect = responses
        sleep_func = Mock()

        client = ViagensAPIClient(
            url="https://example.test/viagens",
            headers={"chave-api-dados": "token"},
            backoff_seconds=2,
            max_retries=2,
            session=session,
            sleep_func=sleep_func,
        )

        response = client._get_with_retry({"pagina": "1"})

        self.assertIs(response, responses[-1])
        self.assertEqual([call.args[0] for call in sleep_func.call_args_list], [2, 4])


if __name__ == "__main__":
    unittest.main()
