import unittest
from datetime import date

from app.backend.main import parse_filters


class FilterParsingTest(unittest.TestCase):
    def test_parse_filters_accepts_textual_reason_filter(self):
        filters = parse_filters(
            data_inicio="2024-05-01",
            data_fim="2026-04-30",
            motivo_contem="reuniao",
            orgao=["35000"],
        )

        self.assertEqual(filters.data_inicio, date(2024, 5, 1))
        self.assertEqual(filters.data_fim, date(2026, 4, 30))
        self.assertEqual(filters.motivo_contem, "reuniao")
        self.assertEqual(filters.orgao, ["35000"])

    def test_parse_filters_accepts_accented_reason_alias(self):
        filters = parse_filters(motivo_contem_alias="missao")

        self.assertEqual(filters.motivo_contem, "missao")

    def test_parse_filters_accepts_org_name_for_drilldown(self):
        filters = parse_filters(orgao_nome="Ministerio das Relacoes Exteriores")

        self.assertEqual(filters.orgao_nome, "Ministerio das Relacoes Exteriores")


if __name__ == "__main__":
    unittest.main()
