import uuid
from datetime import datetime, timezone

from api import config
from api.csv_store import CSVReadError, CSVWriteError, read_products, write_products
from api.schemas import Product, ProductCreate, StockTransfer, StockUpdate, Store, TransferResult


class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class DuplicateProductError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ProductNotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class StoreNotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class StockConflictError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class PersistenceError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _parse_product(row: dict) -> Product:
    return Product(
        product_id=row["product_id"],
        store_id=row["store_id"],
        name=row["name"],
        quantity=int(row["quantity"]),
        unit=row["unit"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _load_products() -> list[dict]:
    try:
        return read_products(config.PRODUCTS_CSV_PATH)
    except CSVReadError as exc:
        raise PersistenceError(str(exc)) from exc


def _save_products(rows: list[dict]) -> None:
    try:
        write_products(config.PRODUCTS_CSV_PATH, rows)
    except CSVWriteError as exc:
        raise PersistenceError(str(exc)) from exc


def _validate_store_id(store_id: str) -> str:
    normalized = store_id.strip()
    if normalized not in config.STORE_IDS:
        raise StoreNotFoundError(
            f"Store '{store_id}' was not found. Valid stores: {', '.join(config.STORE_IDS)}."
        )
    return normalized


def list_stores() -> list[Store]:
    return [Store(store_id=store_id) for store_id in config.STORE_IDS]


def list_inventory(store_id: str | None = None) -> list[Product]:
    rows = _load_products()
    if store_id is not None:
        store = _validate_store_id(store_id)
        rows = [row for row in rows if row["store_id"] == store]
    return [_parse_product(row) for row in rows]


def create_product(payload: ProductCreate) -> Product:
    store_id = _validate_store_id(payload.store_id)
    name = payload.name.strip()
    unit = payload.unit.strip()
    if not name or not unit:
        raise ValidationError("name and unit are required and cannot be blank.")
    if payload.quantity < 0:
        raise ValidationError("quantity must be zero or greater.")

    rows = _load_products()
    normalized_name = name.casefold()
    if any(
        row["store_id"] == store_id and row["name"].casefold() == normalized_name
        for row in rows
    ):
        raise DuplicateProductError(
            f"A product named '{name}' already exists in store '{store_id}'."
        )

    timestamp = _now_iso()
    product = {
        "product_id": str(uuid.uuid4()),
        "store_id": store_id,
        "name": name,
        "quantity": str(payload.quantity),
        "unit": unit,
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    rows.append(product)
    _save_products(rows)
    return _parse_product(product)


def update_stock(product_id: str, payload: StockUpdate) -> Product:
    if payload.delta == 0:
        raise ValidationError("delta must be a non-zero integer.")

    rows = _load_products()
    for index, row in enumerate(rows):
        if row["product_id"] != product_id:
            continue

        current_quantity = int(row["quantity"])
        new_quantity = current_quantity + payload.delta
        if new_quantity < 0:
            raise StockConflictError(
                f"Stock update would reduce '{row['name']}' below zero."
            )

        row["quantity"] = str(new_quantity)
        row["updated_at"] = _now_iso()
        rows[index] = row
        _save_products(rows)
        return _parse_product(row)

    raise ProductNotFoundError(f"Product '{product_id}' was not found.")


def get_store_inventory(store_id: str) -> list[Product]:
    return list_inventory(store_id=store_id)


def delete_product(product_id: str) -> Product:
    rows = _load_products()
    for index, row in enumerate(rows):
        if row["product_id"] != product_id:
            continue
        deleted = _parse_product(row)
        del rows[index]
        _save_products(rows)
        return deleted

    raise ProductNotFoundError(f"Product '{product_id}' was not found.")


def transfer_stock(payload: StockTransfer) -> TransferResult:
    to_store_id = _validate_store_id(payload.to_store_id)
    rows = _load_products()
    source_index = None
    source_row = None
    for index, row in enumerate(rows):
        if row["product_id"] == payload.product_id:
            source_index = index
            source_row = row
            break

    if source_row is None:
        raise ProductNotFoundError(f"Product '{payload.product_id}' was not found.")

    from_store_id = source_row["store_id"]
    if from_store_id == to_store_id:
        raise ValidationError("Cannot transfer stock to the same store.")

    source_quantity = int(source_row["quantity"])
    if payload.quantity > source_quantity:
        raise StockConflictError(
            f"Cannot transfer {payload.quantity} units; only {source_quantity} available."
        )

    normalized_name = source_row["name"].casefold()
    destination_index = None
    for index, row in enumerate(rows):
        if row["store_id"] != to_store_id:
            continue
        if row["name"].casefold() != normalized_name:
            continue
        if row["unit"] != source_row["unit"]:
            raise ValidationError(
                f"Destination store already has '{row['name']}' with unit "
                f"'{row['unit']}', which differs from source unit '{source_row['unit']}'."
            )
        destination_index = index
        break

    timestamp = _now_iso()
    source_row["quantity"] = str(source_quantity - payload.quantity)
    source_row["updated_at"] = timestamp
    rows[source_index] = source_row

    if destination_index is None:
        destination_row = {
            "product_id": str(uuid.uuid4()),
            "store_id": to_store_id,
            "name": source_row["name"],
            "quantity": str(payload.quantity),
            "unit": source_row["unit"],
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        rows.append(destination_row)
    else:
        destination_row = rows[destination_index]
        destination_row["quantity"] = str(
            int(destination_row["quantity"]) + payload.quantity
        )
        destination_row["updated_at"] = timestamp
        rows[destination_index] = destination_row

    _save_products(rows)
    return TransferResult(
        from_store_id=from_store_id,
        to_store_id=to_store_id,
        quantity=payload.quantity,
        source_product=_parse_product(source_row),
        destination_product=_parse_product(destination_row),
    )


def get_low_stock_alerts(
    threshold: int | None = None, store_id: str | None = None
) -> list[Product]:
    limit = config.LOW_STOCK_THRESHOLD if threshold is None else threshold
    rows = _load_products()
    if store_id is not None:
        store = _validate_store_id(store_id)
        rows = [row for row in rows if row["store_id"] == store]
    alerts = [
        _parse_product(row)
        for row in rows
        if int(row["quantity"]) < limit
    ]
    return sorted(alerts, key=lambda product: (product.store_id, product.quantity))
