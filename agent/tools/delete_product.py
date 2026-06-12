from typing import Any

from agent import api_client
from agent.tools.base import Tool

NAME = "delete_product"

DEFINITION: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": NAME,
        "description": (
            "Permanently delete a product from inventory, removing its entire row. "
            "Use when the owner wants to remove or delete a product completely. "
            "Never use update_stock to zero out quantity as a substitute for deletion."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string"},
            },
            "required": ["product_id"],
        },
    },
}


def run(arguments: dict[str, Any]) -> Any:
    return api_client.delete_product(product_id=str(arguments["product_id"]))


TOOL = Tool(name=NAME, definition=DEFINITION, run=run, inventory_mutation=True)
