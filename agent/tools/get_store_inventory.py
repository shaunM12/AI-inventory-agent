from typing import Any

from agent import api_client
from agent.tools.base import Tool

NAME = "get_store_inventory"

DEFINITION: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": NAME,
        "description": (
            "Return inventory for a single store. Use when the owner asks about one "
            "location (Henderson or Las Vegas) rather than all stores."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "store_id": {
                    "type": "string",
                    "description": "Store ID: henderson (Henderson, NV) or las-vegas (Las Vegas, NV)",
                }
            },
            "required": ["store_id"],
        },
    },
}


def run(arguments: dict[str, Any]) -> Any:
    return api_client.get_store_inventory(store_id=str(arguments["store_id"]))


TOOL = Tool(name=NAME, definition=DEFINITION, run=run, inventory_display=True)
