from typing import Any

from agent import api_client
from agent.tools.base import Tool

NAME = "list_stores"

DEFINITION: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": NAME,
        "description": "Return the list of store IDs managed by this inventory system",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}


def run(_arguments: dict[str, Any]) -> Any:
    return api_client.list_stores()


TOOL = Tool(name=NAME, definition=DEFINITION, run=run)
