import csv
from io import StringIO
import unittest

from app.backend.csv_export import csv_headers
from app.backend.csv_export import rows_to_csv


class CSVExportTest(unittest.TestCase):
    def test_rows_to_csv_writes_header_and_escapes_values(self):
        content = rows_to_csv(
            [
                {
                    "id": 1,
                    "motivo": "Reuniao, alinhamento",
                    "extra": "ignorado",
                }
            ],
            ["id", "motivo"],
        )

        parsed = list(csv.DictReader(StringIO(content)))
        self.assertEqual(parsed, [{"id": "1", "motivo": "Reuniao, alinhamento"}])
        self.assertTrue(content.startswith("id,motivo"))

    def test_csv_headers_sets_attachment_filename(self):
        self.assertEqual(
            csv_headers("trips.csv"),
            {"Content-Disposition": 'attachment; filename="trips.csv"'},
        )


if __name__ == "__main__":
    unittest.main()
