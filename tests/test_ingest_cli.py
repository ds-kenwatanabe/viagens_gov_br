import unittest
from argparse import ArgumentTypeError

from src.ingest import build_params


class IngestCliTest(unittest.TestCase):
    def test_build_params_converts_iso_dates_to_api_format(self):
        params = build_params(
            data_inicio="2023-01-01",
            data_fim="2023-01-31",
            orgao="20000",
        )

        self.assertEqual(
            params,
            {
                "dataIdaDe": "01/01/2023",
                "dataIdaAte": "31/01/2023",
                "dataRetornoDe": "01/01/2023",
                "dataRetornoAte": "31/01/2023",
                "codigoOrgao": "20000",
                "pagina": "1",
            },
        )

    def test_build_params_rejects_inverted_period(self):
        with self.assertRaises(ArgumentTypeError):
            build_params(
                data_inicio="2023-01-31",
                data_fim="2023-01-01",
                orgao="20000",
            )


if __name__ == "__main__":
    unittest.main()
