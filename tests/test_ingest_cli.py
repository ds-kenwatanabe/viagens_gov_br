import unittest
from argparse import ArgumentTypeError

from src.ingest import build_params
from src.ingest import build_monthly_windows
from src.ingest import parse_orgaos


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

    def test_build_monthly_windows_splits_long_period(self):
        windows = build_monthly_windows("2024-05-15", "2024-07-10")

        self.assertEqual(
            windows,
            [
                ("2024-05-15", "2024-05-31"),
                ("2024-06-01", "2024-06-30"),
                ("2024-07-01", "2024-07-10"),
            ],
        )

    def test_parse_orgaos_accepts_single_and_batch_values(self):
        orgaos = parse_orgaos("20000", "22000,26000,20000")

        self.assertEqual(orgaos, ["20000", "22000", "26000"])


if __name__ == "__main__":
    unittest.main()
