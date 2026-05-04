import unittest
from unittest.mock import Mock

from src.api_client import ViagensAPIClient


class ViagensAPIClientTest(unittest.TestCase):
    def test_fetch_page_uses_page_copy_without_mutating_params(self):
        response = Mock()
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


if __name__ == "__main__":
    unittest.main()
