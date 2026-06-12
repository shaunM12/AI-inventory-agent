from agent.tools.registry import INVENTORY_MUTATION_TOOL_NAMES, INVENTORY_TOOL_NAMES, TOOL_REGISTRY, run_tool


def test_tool_registry_has_unique_names():
    names = [tool.name for tool in TOOL_REGISTRY.values()]
    assert len(names) == len(set(names))


def test_inventory_tool_names_match_registry_flags():
    for tool in TOOL_REGISTRY.values():
        if tool.inventory_display:
            assert tool.name in INVENTORY_TOOL_NAMES
        else:
            assert tool.name not in INVENTORY_TOOL_NAMES


def test_inventory_mutation_tool_names_match_registry_flags():
    expected = {
        "create_product",
        "update_stock",
        "delete_product",
        "transfer_stock",
    }
    assert INVENTORY_MUTATION_TOOL_NAMES == expected
