import csv
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api import config, inventory_service
from api.app import app

STORE_A = "henderson"
STORE_B = "las-vegas"


@pytest.fixture()
def products_csv(tmp_path, monkeypatch):
    csv_path = tmp_path / "products.csv"
    monkeypatch.setattr(config, "PRODUCTS_CSV_PATH", str(csv_path))
    monkeypatch.setattr(config, "STORE_IDS", [STORE_A, STORE_B])
    return csv_path


@pytest.fixture()
def client(products_csv):
    return TestClient(app)


def test_get_stores_returns_both_stores(client):
    response = client.get("/stores")

    assert response.status_code == 200
    assert response.json() == [
        {"store_id": STORE_A},
        {"store_id": STORE_B},
    ]


def test_get_inventory_returns_all_rows(client, products_csv):
    with products_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=config.PRODUCT_COLUMNS)
        writer.writeheader()
        writer.writerow(
            {
                "product_id": "prod-1",
                "store_id": STORE_A,
                "name": "Oat Milk",
                "quantity": "5",
                "unit": "units",
                "created_at": "2026-06-12T10:00:00+00:00",
                "updated_at": "2026-06-12T10:00:00+00:00",
            }
        )

    response = client.get("/inventory")

    assert response.status_code == 200
    assert response.json() == [
        {
            "product_id": "prod-1",
            "store_id": STORE_A,
            "name": "Oat Milk",
            "quantity": 5,
            "unit": "units",
            "created_at": "2026-06-12T10:00:00Z",
            "updated_at": "2026-06-12T10:00:00Z",
        }
    ]


def test_get_inventory_filters_by_store(client):
    client.post(
        "/inventory",
        json={
            "store_id": STORE_A,
            "name": "Oat Milk",
            "quantity": 30,
            "unit": "units",
        },
    )
    client.post(
        "/inventory",
        json={
            "store_id": STORE_B,
            "name": "Oat Milk",
            "quantity": 12,
            "unit": "units",
        },
    )

    response = client.get("/inventory", params={"store_id": STORE_B})

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["store_id"] == STORE_B


def test_post_inventory_creates_product(client):
    response = client.post(
        "/inventory",
        json={
            "store_id": STORE_A,
            "name": "Oat Milk",
            "quantity": 30,
            "unit": "units",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["store_id"] == STORE_A
    assert body["name"] == "Oat Milk"
    assert body["quantity"] == 30
    assert body["unit"] == "units"
    assert body["product_id"]


def test_patch_inventory_applies_positive_delta(client):
    create_response = client.post(
        "/inventory",
        json={
            "store_id": STORE_A,
            "name": "Arabica",
            "quantity": 10,
            "unit": "bags",
        },
    )
    product_id = create_response.json()["product_id"]

    response = client.patch(f"/inventory/{product_id}", json={"delta": 5})

    assert response.status_code == 200
    assert response.json()["quantity"] == 15


def test_patch_inventory_applies_negative_delta(client):
    create_response = client.post(
        "/inventory",
        json={
            "store_id": STORE_A,
            "name": "Arabica",
            "quantity": 20,
            "unit": "bags",
        },
    )
    product_id = create_response.json()["product_id"]

    response = client.patch(f"/inventory/{product_id}", json={"delta": -12})

    assert response.status_code == 200
    assert response.json()["quantity"] == 8


def test_patch_inventory_rejects_stock_below_zero(client):
    create_response = client.post(
        "/inventory",
        json={
            "store_id": STORE_A,
            "name": "Arabica",
            "quantity": 5,
            "unit": "bags",
        },
    )
    product_id = create_response.json()["product_id"]

    response = client.patch(f"/inventory/{product_id}", json={"delta": -12})

    assert response.status_code == 409
    assert "below zero" in response.json()["detail"]


def test_get_inventory_alerts_returns_low_stock_products(client, monkeypatch):
    monkeypatch.setattr(config, "LOW_STOCK_THRESHOLD", 10)
    client.post(
        "/inventory",
        json={"store_id": STORE_A, "name": "Oat Milk", "quantity": 3, "unit": "units"},
    )
    client.post(
        "/inventory",
        json={"store_id": STORE_B, "name": "Arabica", "quantity": 25, "unit": "bags"},
    )

    response = client.get("/inventory/alerts")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Oat Milk"


def test_get_inventory_alerts_filters_by_store(client, monkeypatch):
    monkeypatch.setattr(config, "LOW_STOCK_THRESHOLD", 10)
    client.post(
        "/inventory",
        json={"store_id": STORE_A, "name": "Oat Milk", "quantity": 3, "unit": "units"},
    )
    client.post(
        "/inventory",
        json={"store_id": STORE_B, "name": "Oat Milk", "quantity": 3, "unit": "units"},
    )

    response = client.get("/inventory/alerts", params={"store_id": STORE_B})

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["store_id"] == STORE_B


def test_invalid_requests_return_descriptive_4xx_errors(client):
    missing_fields = client.post("/inventory", json={"name": "Oat Milk"})
    assert missing_fields.status_code == 422

    duplicate = client.post(
        "/inventory",
        json={
            "store_id": STORE_A,
            "name": "Oat Milk",
            "quantity": 10,
            "unit": "units",
        },
    )
    assert duplicate.status_code == 201
    conflict = client.post(
        "/inventory",
        json={
            "store_id": STORE_A,
            "name": "oat milk",
            "quantity": 5,
            "unit": "units",
        },
    )
    assert conflict.status_code == 409
    assert "already exists" in conflict.json()["detail"]

    same_name_other_store = client.post(
        "/inventory",
        json={
            "store_id": STORE_B,
            "name": "Oat Milk",
            "quantity": 5,
            "unit": "units",
        },
    )
    assert same_name_other_store.status_code == 201

    invalid_store = client.get("/inventory", params={"store_id": "unknown-store"})
    assert invalid_store.status_code == 404

    missing_product = client.patch("/inventory/missing-id", json={"delta": 5})
    assert missing_product.status_code == 404

    blank_name = client.post(
        "/inventory",
        json={
            "store_id": STORE_A,
            "name": "   ",
            "quantity": 1,
            "unit": "units",
        },
    )
    assert blank_name.status_code == 400


def test_read_failure_returns_500(client, monkeypatch):
    def fail_load():
        raise inventory_service.PersistenceError("Failed to read products CSV: disk error")

    monkeypatch.setattr(inventory_service, "_load_products", fail_load)

    response = client.get("/inventory")

    assert response.status_code == 500
    assert "disk error" in response.json()["detail"]


def test_get_store_inventory_returns_one_store(client):
    client.post(
        "/inventory",
        json={"store_id": STORE_A, "name": "Oat Milk", "quantity": 30, "unit": "units"},
    )
    client.post(
        "/inventory",
        json={"store_id": STORE_B, "name": "Oat Milk", "quantity": 12, "unit": "units"},
    )

    response = client.get(f"/stores/{STORE_A}/inventory")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["store_id"] == STORE_A


def test_get_store_inventory_rejects_unknown_store(client):
    response = client.get("/stores/unknown-store/inventory")

    assert response.status_code == 404


def test_delete_inventory_removes_product(client):
    create_response = client.post(
        "/inventory",
        json={"store_id": STORE_A, "name": "Oat Milk", "quantity": 10, "unit": "units"},
    )
    product_id = create_response.json()["product_id"]

    response = client.delete(f"/inventory/{product_id}")

    assert response.status_code == 200
    assert response.json()["product_id"] == product_id
    assert client.get("/inventory").json() == []


def test_delete_inventory_returns_404_for_missing_product(client):
    response = client.delete("/inventory/missing-id")

    assert response.status_code == 404


def test_transfer_stock_moves_quantity_to_new_destination_product(client):
    create_response = client.post(
        "/inventory",
        json={"store_id": STORE_A, "name": "Oat Milk", "quantity": 20, "unit": "units"},
    )
    product_id = create_response.json()["product_id"]

    response = client.post(
        "/inventory/transfer",
        json={"product_id": product_id, "to_store_id": STORE_B, "quantity": 8},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["from_store_id"] == STORE_A
    assert body["to_store_id"] == STORE_B
    assert body["quantity"] == 8
    assert body["source_product"]["quantity"] == 12
    assert body["destination_product"]["store_id"] == STORE_B
    assert body["destination_product"]["quantity"] == 8


def test_transfer_stock_merges_with_existing_destination_product(client):
    source_response = client.post(
        "/inventory",
        json={"store_id": STORE_A, "name": "Oat Milk", "quantity": 15, "unit": "units"},
    )
    destination_response = client.post(
        "/inventory",
        json={"store_id": STORE_B, "name": "Oat Milk", "quantity": 5, "unit": "units"},
    )
    product_id = source_response.json()["product_id"]
    destination_id = destination_response.json()["product_id"]

    response = client.post(
        "/inventory/transfer",
        json={"product_id": product_id, "to_store_id": STORE_B, "quantity": 6},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source_product"]["quantity"] == 9
    assert body["destination_product"]["product_id"] == destination_id
    assert body["destination_product"]["quantity"] == 11


def test_transfer_stock_rejects_insufficient_quantity(client):
    create_response = client.post(
        "/inventory",
        json={"store_id": STORE_A, "name": "Oat Milk", "quantity": 4, "unit": "units"},
    )
    product_id = create_response.json()["product_id"]

    response = client.post(
        "/inventory/transfer",
        json={"product_id": product_id, "to_store_id": STORE_B, "quantity": 10},
    )

    assert response.status_code == 409


def test_transfer_stock_rejects_same_store(client):
    create_response = client.post(
        "/inventory",
        json={"store_id": STORE_A, "name": "Oat Milk", "quantity": 10, "unit": "units"},
    )
    product_id = create_response.json()["product_id"]

    response = client.post(
        "/inventory/transfer",
        json={"product_id": product_id, "to_store_id": STORE_A, "quantity": 5},
    )

    assert response.status_code == 400
