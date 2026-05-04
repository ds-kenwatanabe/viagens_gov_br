import unittest
from unittest.mock import MagicMock
from unittest.mock import Mock

from src.database import insert_viagem


class DatabaseTest(unittest.TestCase):
    def test_insert_viagem_uses_on_conflict_and_returns_insert_status(self):
        cursor = Mock()
        cursor.fetchone.return_value = (123,)

        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cursor

        inserted = insert_viagem(conn, {"id": 123})

        sql = cursor.execute.call_args.args[0]
        self.assertIn("ON CONFLICT (id) DO NOTHING", sql)
        self.assertIn("RETURNING id", sql)
        self.assertTrue(inserted)

    def test_insert_viagem_returns_false_when_row_conflicts(self):
        cursor = Mock()
        cursor.fetchone.return_value = None

        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cursor

        inserted = insert_viagem(conn, {"id": 123})

        self.assertFalse(inserted)


if __name__ == "__main__":
    unittest.main()
