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


if __name__ == "__main__":
    unittest.main()
