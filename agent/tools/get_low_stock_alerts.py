from typing import Any

from agent import api_client
from agent.tools.base import Tool

NAME = "get_low_stock_alerts"

DEFINITION: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": NAME,
        "description": (
            "Return products whose quantity is below the configured low-stock threshold. "
            "Omit store_id for all stores, or pass a store_id to filter one store."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "store_id": {
                    "type": "string",
                    "description": "Optional store ID: henderson (Henderson, NV) or las-vegas (Las Vegas, NV)",
                }
            },
            "required": [],
        },
    },
}


def run(arguments: dict[str, Any]) -> Any:
    return api_client.get_low_stock_alerts(store_id=arguments.get("store_id"))


TOOL = Tool(name=NAME, definition=DEFINITION, run=run, inventory_display=True)
