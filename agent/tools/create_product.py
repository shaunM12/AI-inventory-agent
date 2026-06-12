from typing import Any

from agent import api_client
from agent.tools.base import Tool

NAME = "create_product"

DEFINITION: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": NAME,
        "description": "Add a new product to a specific store with its starting quantity and unit",
        "parameters": {
            "type": "object",
            "properties": {
                "store_id": {"type": "string"},
                "name": {"type": "string"},
                "quantity": {"type": "number"},
                "unit": {"type": "string"},
            },
            "required": ["store_id", "name", "quantity", "unit"],
        },
    },
}


def run(arguments: dict[str, Any]) -> Any:
    return api_client.create_product(
        store_id=str(arguments["store_id"]),
        name=str(arguments["name"]),
        quantity=arguments["quantity"],
        unit=str(arguments["unit"]),
    )


TOOL = Tool(name=NAME, definition=DEFINITION, run=run, inventory_mutation=True)
