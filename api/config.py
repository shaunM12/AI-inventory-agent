import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", "10"))
PRODUCTS_CSV_PATH = os.getenv(
    "PRODUCTS_CSV_PATH", str(PROJECT_ROOT / "data" / "products.csv")
)
CONVERSATION_LOG_CSV_PATH = os.getenv(
    "CONVERSATION_LOG_CSV_PATH",
    str(PROJECT_ROOT / "data" / "conversation_log.csv"),
)
STORE_IDS = [
    store.strip()
    for store in os.getenv("STORE_IDS", "henderson,las-vegas").split(",")
    if store.strip()
]

PRODUCT_COLUMNS = [
    "product_id",
    "store_id",
    "name",
    "quantity",
    "unit",
    "created_at",
    "updated_at",
]
