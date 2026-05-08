import unittest
from datetime import date
from unittest.mock import Mock
from unittest.mock import patch

from app.backend import queries
from app.backend.schemas import FilterParams


class QueryBuilderTest(unittest.TestCase):
    def test_build_where_includes_dashboard_filters(self):
        where_sql, params = queries._build_where(
            FilterParams(
                orgao=["35000"],
                orgao_nome="Ministerio das Relacoes Exteriores",
                beneficiario="Mauro",
                cargo="Ministro",
                motivo_contem="reuniao",
                tipo_viagem="Internacional",
                data_inicio=date(2024, 5, 1),
                data_fim=date(2026, 4, 30),
            ),
            table_alias="v",
        )

        self.assertIn("v.orgao_codigo_siafi = ANY(%s)", where_sql)
        self.assertIn("v.orgao_nome = %s", where_sql)
        self.assertIn("v.beneficiario_nome ILIKE %s", where_sql)
        self.assertIn("v.cargo_descricao ILIKE %s", where_sql)
        self.assertIn("v.motivo ILIKE %s", where_sql)
        self.assertIn("v.tipo_viagem = %s", where_sql)
        self.assertEqual(
            params,
            [
                ["35000"],
                "Ministerio das Relacoes Exteriores",
                "%Mauro%",
                "%Ministro%",
                "%reuniao%",
                "Internacional",
                date(2024, 5, 1),
                date(2026, 4, 30),
            ],
        )

    def test_get_trip_locations_queries_by_trip_id(self):
        cursor = Mock()
        cursor.fetchall.return_value = [
            {
                "local_texto": "Lisboa",
                "cidade": "Lisboa",
                "estado": None,
                "pais": "Portugal",
                "latitude": 38.722252,
                "longitude": -9.139337,
                "confidence": 1.0,
                "fonte": "local",
            }
        ]
        context = Mock()
        context.__enter__ = Mock(return_value=cursor)
        context.__exit__ = Mock(return_value=None)

        with patch.object(queries, "get_cursor", return_value=context):
            rows = queries.get_trip_locations(497726197)

        self.assertEqual(rows[0]["cidade"], "Lisboa")
        self.assertEqual(cursor.execute.call_args.args[1], [497726197])
        self.assertIn("FROM viagem_localidades", cursor.execute.call_args.args[0])

    def test_get_map_city_summary_groups_by_city(self):
        cursor = Mock()
        cursor.fetchall.return_value = []
        context = Mock()
        context.__enter__ = Mock(return_value=cursor)
        context.__exit__ = Mock(return_value=None)

        with patch.object(queries, "get_cursor", return_value=context):
            queries.get_map_summary(FilterParams(), group_by="city", limit=50)

        sql = cursor.execute.call_args.args[0]
        params = cursor.execute.call_args.args[1]
        self.assertIn("'city' AS group_by", sql)
        self.assertIn("GROUP BY cidade, estado, pais, latitude, longitude", sql)
        self.assertEqual(params, [50])

    def test_get_map_country_summary_groups_by_country(self):
        cursor = Mock()
        cursor.fetchall.return_value = []
        context = Mock()
        context.__enter__ = Mock(return_value=cursor)
        context.__exit__ = Mock(return_value=None)

        with patch.object(queries, "get_cursor", return_value=context):
            queries.get_map_summary(FilterParams(), group_by="country", limit=25)

        sql = cursor.execute.call_args.args[0]
        params = cursor.execute.call_args.args[1]
        self.assertIn("'country' AS group_by", sql)
        self.assertIn("GROUP BY pais", sql)
        self.assertEqual(params, [25])

    def test_org_beneficiary_trip_export_builds_hierarchical_query(self):
        cursor = Mock()
        cursor.fetchall.return_value = []
        context = Mock()
        context.__enter__ = Mock(return_value=cursor)
        context.__exit__ = Mock(return_value=None)

        filters = FilterParams(
            orgao=["35000"],
            beneficiario="Maria",
            data_inicio=date(2026, 4, 1),
            data_fim=date(2026, 4, 30),
        )

        with patch.object(queries, "get_cursor", return_value=context):
            queries.get_org_beneficiary_trip_export(filters, limit=10)

        sql = cursor.execute.call_args.args[0]
        params = cursor.execute.call_args.args[1]
        self.assertIn("WITH selected AS", sql)
        self.assertIn("COUNT(*) OVER", sql)
        self.assertIn("id AS viagem_id", sql)
        self.assertIn("beneficiario_numero_viagens", sql)
        self.assertIn("PARTITION BY orgao_nome, beneficiario_nome", sql)
        self.assertEqual(
            params,
            [["35000"], "%Maria%", date(2026, 4, 1), date(2026, 4, 30), 10],
        )

    def test_outlier_query_supports_new_kinds(self):
        cases = {
            "beneficiario_mes": "ROW_NUMBER() OVER (PARTITION BY periodo",
            "orgao_aumento_mensal": "LAG(valor_total)",
            "internacionais_caras": "tipo_viagem = 'Internacional'",
            "passagem_alta_diaria_baixa": "valor_total_passagem",
            "acima_percentis": "percentile_cont(0.95)",
        }

        for kind, expected_sql in cases.items():
            with self.subTest(kind=kind):
                query = queries._outlier_query(kind, "WHERE 1 = 1")
                self.assertIn(expected_sql, query)
                self.assertIn("LIMIT %s", query)


if __name__ == "__main__":
    unittest.main()
