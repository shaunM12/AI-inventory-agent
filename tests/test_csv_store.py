import csv

from api import config
from api.csv_store import READABLE_COLUMN_ORDER, format_products_table, read_products, write_products


def test_write_products_uses_readable_csv_format(tmp_path):
    path = tmp_path / "products.csv"
    rows = [
        {
            "product_id": "prod-1",
            "store_id": "henderson",
            "name": "Oat Milk",
            "quantity": "18",
            "unit": "cartons",
            "created_at": "2026-06-12T20:00:00+00:00",
            "updated_at": "2026-06-12T20:00:00+00:00",
        }
    ]

    write_products(str(path), rows)
    content = path.read_text(encoding="utf-8")

    assert content.startswith("store_id,name,quantity,unit,product_id,created_at,updated_at\n")
    assert "henderson,Oat Milk,18,cartons,prod-1" in content
    assert read_products(str(path)) == rows


def test_write_products_sorts_by_store_and_name(tmp_path):
    path = tmp_path / "products.csv"
    rows = [
        {
            "product_id": "2",
            "store_id": "las-vegas",
            "name": "Oat Milk",
            "quantity": "14",
            "unit": "cartons",
            "created_at": "2026-06-12T20:00:00+00:00",
            "updated_at": "2026-06-12T20:00:00+00:00",
        },
        {
            "product_id": "1",
            "store_id": "henderson",
            "name": "Arabica",
            "quantity": "15",
            "unit": "bags",
            "created_at": "2026-06-12T20:00:00+00:00",
            "updated_at": "2026-06-12T20:00:00+00:00",
        },
    ]

    write_products(str(path), rows)
    lines = path.read_text(encoding="utf-8").splitlines()

    assert lines[1].startswith("henderson,Arabica")
    assert lines[2].startswith("las-vegas,Oat Milk")


def test_read_products_supports_legacy_product_id_first_csv(tmp_path):
    path = tmp_path / "products.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=config.PRODUCT_COLUMNS)
        writer.writeheader()
        writer.writerow(
            {
                "product_id": "prod-1",
                "store_id": "henderson",
                "name": "Oat Milk",
                "quantity": "18",
                "unit": "cartons",
                "created_at": "2026-06-12T20:00:00+00:00",
                "updated_at": "2026-06-12T20:00:00+00:00",
            }
        )

    rows = read_products(str(path))

    assert len(rows) == 1
    assert rows[0]["name"] == "Oat Milk"


def test_read_products_supports_grouped_table_format(tmp_path):
    path = tmp_path / "products.csv"
    path.write_text(
        "\n".join(
            [
                "=== store_id: henderson (Henderson, NV) ===",
                "Name     Quantity  Unit",
                "Oat Milk       18  cartons",
                "@ product_id=prod-1 | created_at=2026-06-12T20:00:00+00:00 | updated_at=2026-06-12T20:00:00+00:00",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    rows = read_products(str(path))

    assert rows == [
        {
            "store_id": "henderson",
            "name": "Oat Milk",
            "quantity": "18",
            "unit": "cartons",
            "product_id": "prod-1",
            "created_at": "2026-06-12T20:00:00+00:00",
            "updated_at": "2026-06-12T20:00:00+00:00",
        }
    ]


def test_format_products_table_groups_by_store():
    rows = [
        {
            "product_id": "2",
            "store_id": "las-vegas",
            "name": "Oat Milk",
            "quantity": "14",
            "unit": "cartons",
            "created_at": "2026-06-12T20:00:00+00:00",
            "updated_at": "2026-06-12T20:00:00+00:00",
        },
        {
            "product_id": "1",
            "store_id": "henderson",
            "name": "Arabica",
            "quantity": "15",
            "unit": "bags",
            "created_at": "2026-06-12T20:00:00+00:00",
            "updated_at": "2026-06-12T20:00:00+00:00",
        },
    ]

    rendered = format_products_table(rows)

    assert "=== henderson (Henderson, NV) ===" in rendered
    assert rendered.index("henderson") < rendered.index("las-vegas")
