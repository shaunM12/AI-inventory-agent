import json
from collections import defaultdict
from collections.abc import Callable

from agent.tools import INVENTORY_TOOL_NAMES

STORE_CITY_LABELS = {
    "henderson": "Henderson, NV",
    "las-vegas": "Las Vegas, NV",
}


def parse_product_list(json_str: str) -> list[dict] | None:
    try:
        data = json.loads(json_str)
    except (TypeError, json.JSONDecodeError):
        return None
    if not isinstance(data, list):
        return None
    for item in data:
        if not isinstance(item, dict):
            return None
        if not {"store_id", "name", "quantity", "unit"}.issubset(item.keys()):
            return None
    return data


def _store_section_header(store_id: str) -> str:
    city = STORE_CITY_LABELS.get(store_id)
    if city:
        return f"=== store_id: {store_id} ({city}) ==="
    return f"=== store_id: {store_id} ==="


def format_inventory_by_store(products: list[dict]) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for product in products:
        grouped[str(product["store_id"])].append(product)

    store_order = sorted(
        grouped.keys(),
        key=lambda store_id: (store_id not in STORE_CITY_LABELS, store_id),
    )

    sections: list[str] = []
    for store_id in store_order:
        rows = sorted(grouped[store_id], key=lambda item: str(item["name"]).casefold())
        name_width = max(len("Name"), *(len(str(row["name"])) for row in rows))
        quantity_width = max(
            len("Quantity"),
            *(len(str(row["quantity"])) for row in rows),
        )

        lines = [
            _store_section_header(store_id),
            f"{'Name'.ljust(name_width)}  {'Quantity'.rjust(quantity_width)}  Unit",
        ]
        for row in rows:
            name = str(row["name"])
            quantity = row["quantity"]
            unit = str(row["unit"])
            lines.append(
                f"{name.ljust(name_width)}  {str(quantity).rjust(quantity_width)}  {unit}"
            )
        sections.append("\n".join(lines))

    return "\n\n".join(sections)


def should_print_final_response(
    response: str, table_printed: bool, *, inventory_updated: bool = False
) -> bool:
    stripped = response.strip()
    if not stripped:
        return False
    if table_printed and inventory_updated:
        return False
    if not table_printed:
        return True
    if "**" in stripped:
        return False
    if stripped.count("\n- ") > 2:
        return False
    return True


def resolve_turn_inventory_display(
    mutations_this_turn: int,
    last_inventory_json: str | None,
    fetch_inventory_json: Callable[[], str],
) -> tuple[str | None, bool]:
    if mutations_this_turn > 0:
        return fetch_inventory_json(), True
    if last_inventory_json:
        return last_inventory_json, False
    return None, False


def format_message_for_log(actor: str, message: str, tool_call: str = "") -> str:
    if actor == "tool" and tool_call in INVENTORY_TOOL_NAMES:
        products = parse_product_list(message)
        if products:
            return format_inventory_by_store(products)
    return message


def maybe_print_inventory_table(tool_name: str, tool_result: str) -> bool:
    if tool_name not in INVENTORY_TOOL_NAMES:
        return False

    products = parse_product_list(tool_result)
    if not products:
        return False

    print(format_inventory_by_store(products))
    print()
    return True


def print_inventory_refresh(inventory_json: str) -> bool:
    return maybe_print_inventory_table("list_inventory", inventory_json)
