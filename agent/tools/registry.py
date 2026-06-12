import json
from typing import Any

from agent.tools.base import Tool
from agent.tools.create_product import TOOL as CREATE_PRODUCT
from agent.tools.delete_product import TOOL as DELETE_PRODUCT
from agent.tools.get_low_stock_alerts import TOOL as GET_LOW_STOCK_ALERTS
from agent.tools.get_store_inventory import TOOL as GET_STORE_INVENTORY
from agent.tools.list_inventory import TOOL as LIST_INVENTORY
from agent.tools.list_stores import TOOL as LIST_STORES
from agent.tools.transfer_stock import TOOL as TRANSFER_STOCK
from agent.tools.update_stock import TOOL as UPDATE_STOCK

ALL_TOOLS: tuple[Tool, ...] = (
    LIST_STORES,
    GET_STORE_INVENTORY,
    LIST_INVENTORY,
    CREATE_PRODUCT,
    UPDATE_STOCK,
    DELETE_PRODUCT,
    TRANSFER_STOCK,
    GET_LOW_STOCK_ALERTS,
)

TOOL_REGISTRY: dict[str, Tool] = {tool.name: tool for tool in ALL_TOOLS}

TOOL_DEFINITIONS: list[dict[str, Any]] = [tool.definition for tool in ALL_TOOLS]

INVENTORY_TOOL_NAMES: frozenset[str] = frozenset(
    tool.name for tool in ALL_TOOLS if tool.inventory_display
)

INVENTORY_MUTATION_TOOL_NAMES: frozenset[str] = frozenset(
    tool.name for tool in ALL_TOOLS if tool.inventory_mutation
)


def run_tool(name: str, arguments: dict[str, Any]) -> str:
    tool = TOOL_REGISTRY.get(name)
    if tool is None:
        raise RuntimeError(f"Unknown tool: {name}")
    result = tool.run(arguments)
    return json.dumps(result, default=str)
