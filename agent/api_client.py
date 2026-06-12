from typing import Any

import httpx

from agent import config


def api_request(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> Any:
    url = f"{config.API_BASE_URL}{path}"
    with httpx.Client(timeout=30.0) as client:
        response = client.request(method, url, json=payload, params=params)
    if response.status_code >= 400:
        detail = response.text
        try:
            detail = response.json().get("detail", detail)
        except ValueError:
            pass
        raise RuntimeError(f"API {method} {path} failed ({response.status_code}): {detail}")
    if response.status_code == 204 or not response.content:
        return None
    return response.json()


def list_stores() -> Any:
    return api_request("GET", "/stores")


def list_inventory(store_id: str | None = None) -> Any:
    params = {"store_id": store_id} if store_id else None
    return api_request("GET", "/inventory", params=params)


def get_store_inventory(store_id: str) -> Any:
    return api_request("GET", f"/stores/{store_id}/inventory")


def create_product(store_id: str, name: str, quantity: float, unit: str) -> Any:
    return api_request(
        "POST",
        "/inventory",
        {
            "store_id": store_id,
            "name": name,
            "quantity": int(quantity),
            "unit": unit,
        },
    )


def update_stock(product_id: str, delta: float) -> Any:
    return api_request(
        "PATCH",
        f"/inventory/{product_id}",
        {"delta": int(delta)},
    )


def delete_product(product_id: str) -> Any:
    return api_request("DELETE", f"/inventory/{product_id}")


def transfer_stock(product_id: str, to_store_id: str, quantity: float) -> Any:
    return api_request(
        "POST",
        "/inventory/transfer",
        {
            "product_id": product_id,
            "to_store_id": to_store_id,
            "quantity": int(quantity),
        },
    )


def get_low_stock_alerts(store_id: str | None = None) -> Any:
    params = {"store_id": store_id} if store_id else None
    return api_request("GET", "/inventory/alerts", params=params)
