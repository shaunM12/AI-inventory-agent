import csv
import os
import re
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

from api.config import PRODUCT_COLUMNS

READABLE_COLUMN_ORDER = [
    "store_id",
    "name",
    "quantity",
    "unit",
    "product_id",
    "created_at",
    "updated_at",
]

STORE_CITY_LABELS = {
    "henderson": "Henderson, NV",
    "las-vegas": "Las Vegas, NV",
}

STORE_HEADER_PATTERN = re.compile(r"^=== store_id: (\S+)")
PRODUCT_ROW_PATTERN = re.compile(r"^(.+?)  +(\d+)  +(\S+)\s*$")
METADATA_PATTERN = re.compile(
    r"^@ product_id=(.+?) \| created_at=(.+?) \| updated_at=(.+?)\s*$"
)


class CSVReadError(Exception):
    pass


class CSVWriteError(Exception):
    pass


def _ensure_parent_dir(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def _normalize_row(row: dict[str, Any]) -> dict[str, str]:
    return {column: str(row[column]) for column in PRODUCT_COLUMNS}


def _sort_rows(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized = [_normalize_row(row) for row in rows]
    return sorted(
        normalized,
        key=lambda row: (row["store_id"], row["name"].casefold(), row["product_id"]),
    )


def _read_legacy_csv(path: str) -> list[dict[str, Any]]:
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames not in (PRODUCT_COLUMNS, READABLE_COLUMN_ORDER):
            raise CSVReadError(
                f"Invalid CSV headers in {path}. Expected {READABLE_COLUMN_ORDER}."
            )
        return [dict(row) for row in reader]


def _read_grouped_table_file(path: str) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as handle:
        lines = [line.rstrip("\n") for line in handle]

    rows: list[dict[str, Any]] = []
    current_store_id: str | None = None
    pending: dict[str, str] | None = None

    for line in lines:
        if not line.strip():
            continue

        store_match = STORE_HEADER_PATTERN.match(line)
        if store_match:
            current_store_id = store_match.group(1)
            continue

        if line.startswith("Name") and "Quantity" in line and "Unit" in line:
            continue

        metadata_match = METADATA_PATTERN.match(line)
        if metadata_match:
            if pending is None or current_store_id is None:
                raise CSVReadError(f"Metadata line without product row: {line}")
            pending["product_id"] = metadata_match.group(1)
            pending["created_at"] = metadata_match.group(2)
            pending["updated_at"] = metadata_match.group(3)
            rows.append(pending)
            pending = None
            continue

        product_match = PRODUCT_ROW_PATTERN.match(line)
        if product_match:
            if current_store_id is None:
                raise CSVReadError(f"Product row before store header: {line}")
            if pending is not None:
                raise CSVReadError(f"Missing metadata for product: {pending['name']}")
            pending = {
                "store_id": current_store_id,
                "name": product_match.group(1).strip(),
                "quantity": product_match.group(2),
                "unit": product_match.group(3),
            }
            continue

        raise CSVReadError(f"Unrecognized line in grouped products file: {line}")

    if pending is not None:
        raise CSVReadError(f"Missing metadata for product: {pending['name']}")

    return rows


def _read_flat_pipe_table(path: str) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as handle:
        lines = [line.rstrip("\n") for line in handle if line.strip()]

    if not lines:
        return []

    columns = [part.strip() for part in lines[0].split("|")]
    rows: list[dict[str, Any]] = []
    for line in lines[2:]:
        if re.fullmatch(r"[-| ]+", line):
            continue
        values = [part.strip() for part in line.split("|")]
        if len(values) != len(columns):
            raise CSVReadError(f"Invalid table row: {line}")
        row = dict(zip(columns, values))
        rows.append({column: row[column] for column in PRODUCT_COLUMNS})
    return rows


def _ensure_headers(path: str) -> None:
    _ensure_parent_dir(path)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        write_products(path, [])


def read_products(path: str) -> list[dict[str, Any]]:
    _ensure_parent_dir(path)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return []

    try:
        with open(path, encoding="utf-8") as handle:
            first_line = handle.readline().strip()
    except OSError as exc:
        raise CSVReadError(f"Failed to read products CSV: {exc}") from exc

    try:
        if first_line.startswith("=== store_id:"):
            return _read_grouped_table_file(path)
        if "|" in first_line and not first_line.startswith("product_id,"):
            return _read_flat_pipe_table(path)
        return _read_legacy_csv(path)
    except CSVReadError:
        raise
    except OSError as exc:
        raise CSVReadError(f"Failed to read products CSV: {exc}") from exc


def write_products(path: str, rows: list[dict[str, Any]]) -> None:
    _ensure_parent_dir(path)
    directory = os.path.dirname(os.path.abspath(path)) or "."
    sorted_rows = _sort_rows(rows)
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            delete=False,
            newline="",
            encoding="utf-8",
            dir=directory,
            suffix=".tmp",
        ) as temp_handle:
            writer = csv.DictWriter(
                temp_handle, fieldnames=READABLE_COLUMN_ORDER, lineterminator="\n"
            )
            writer.writeheader()
            for row in sorted_rows:
                writer.writerow({column: row[column] for column in READABLE_COLUMN_ORDER})
            temp_path = temp_handle.name
        os.replace(temp_path, path)
    except OSError as exc:
        if "temp_path" in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise CSVWriteError(f"Failed to write products CSV: {exc}") from exc


def format_products_table(rows: list[dict[str, Any]]) -> str:
    """Return a grouped text preview; the persisted file remains standard CSV."""
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in _sort_rows(rows):
        grouped[row["store_id"]].append(row)

    store_order = sorted(
        grouped.keys(),
        key=lambda store_id: (store_id not in STORE_CITY_LABELS, store_id),
    )
    sections: list[str] = []
    for store_id in store_order:
        store_rows = grouped[store_id]
        name_width = max(len("name"), *(len(row["name"]) for row in store_rows))
        quantity_width = max(
            len("quantity"),
            *(len(row["quantity"]) for row in store_rows),
        )
        city = STORE_CITY_LABELS.get(store_id, store_id)
        lines = [
            f"=== {store_id} ({city}) ===",
            f"{'name'.ljust(name_width)},{'quantity'.rjust(quantity_width)},unit",
        ]
        for row in store_rows:
            lines.append(
                f"{row['name'].ljust(name_width)},"
                f"{row['quantity'].rjust(quantity_width)},"
                f"{row['unit']}"
            )
        sections.append("\n".join(lines))
    return "\n\n".join(sections)
