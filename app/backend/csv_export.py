import csv
from io import StringIO
from typing import Iterable


def rows_to_csv(rows: Iterable[dict], columns: list[str]) -> str:
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(column) for column in columns})
    return buffer.getvalue()


def csv_headers(filename: str) -> dict[str, str]:
    return {"Content-Disposition": f'attachment; filename="{filename}"'}
