from typing import Any

from agent import api_client
from agent.tools.base import Tool

NAME = "list_inventory"

DEFINITION: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": NAME,
        "description": (
            "Return inventory products with current quantities and units across all stores."
        ),
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}


def run(_arguments: dict[str, Any]) -> Any:
    return api_client.list_inventory()


TOOL = Tool(name=NAME, definition=DEFINITION, run=run, inventory_display=True)
