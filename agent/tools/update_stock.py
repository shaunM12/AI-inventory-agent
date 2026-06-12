from typing import Any

from agent import api_client
from agent.tools.base import Tool

NAME = "update_stock"

DEFINITION: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": NAME,
        "description": (
            "Adjust stock for an existing product by a delta value, using positive numbers "
            "for incoming stock and negative numbers for outgoing stock"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string"},
                "delta": {"type": "number"},
            },
            "required": ["product_id", "delta"],
        },
    },
}


def run(arguments: dict[str, Any]) -> Any:
    return api_client.update_stock(
        product_id=str(arguments["product_id"]),
        delta=arguments["delta"],
    )


TOOL = Tool(name=NAME, definition=DEFINITION, run=run, inventory_mutation=True)
