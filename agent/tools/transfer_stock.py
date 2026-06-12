from typing import Any

from agent import api_client
from agent.tools.base import Tool

NAME = "transfer_stock"

DEFINITION: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": NAME,
        "description": (
            "Move stock from one store to another. Decreases quantity at the source store "
            "and adds it to a matching product at the destination store (or creates one)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "Product ID at the source store",
                },
                "to_store_id": {
                    "type": "string",
                    "description": "Destination store ID: henderson or las-vegas",
                },
                "quantity": {
                    "type": "number",
                    "description": "Units to transfer (must be positive and not exceed source stock)",
                },
            },
            "required": ["product_id", "to_store_id", "quantity"],
        },
    },
}


def run(arguments: dict[str, Any]) -> Any:
    return api_client.transfer_stock(
        product_id=str(arguments["product_id"]),
        to_store_id=str(arguments["to_store_id"]),
        quantity=arguments["quantity"],
    )


TOOL = Tool(name=NAME, definition=DEFINITION, run=run, inventory_mutation=True)
