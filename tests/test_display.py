import json

from agent.display import (
    format_inventory_by_store,
    format_message_for_log,
    maybe_print_inventory_table,
    parse_product_list,
    print_inventory_refresh,
    resolve_turn_inventory_display,
    should_print_final_response,
)


def test_parse_product_list_accepts_inventory_json():
    payload = json.dumps(
        [
            {
                "product_id": "1",
                "store_id": "henderson",
                "name": "Oat Milk",
                "quantity": 18,
                "unit": "cartons",
            }
        ]
    )

    products = parse_product_list(payload)

    assert products is not None
    assert len(products) == 1


def test_parse_product_list_rejects_non_inventory_json():
    assert parse_product_list('{"detail":"not found"}') is None
    assert parse_product_list("not-json") is None


def test_format_inventory_by_store_groups_and_sorts():
    products = [
        {
            "store_id": "las-vegas",
            "name": "Oat Milk",
            "quantity": 14,
            "unit": "cartons",
        },
        {
            "store_id": "henderson",
            "name": "Arabica",
            "quantity": 15,
            "unit": "bags",
        },
        {
            "store_id": "henderson",
            "name": "Oat Milk",
            "quantity": 18,
            "unit": "cartons",
        },
    ]

    rendered = format_inventory_by_store(products)

    assert "=== store_id: henderson (Henderson, NV) ===" in rendered
    assert "=== store_id: las-vegas (Las Vegas, NV) ===" in rendered
    assert "Quantity" in rendered
    assert "Qty" not in rendered
    assert "Arabica" in rendered
    assert "Oat Milk" in rendered
    assert rendered.index("store_id: henderson") < rendered.index("store_id: las-vegas")
    henderson_section = rendered.split("store_id: las-vegas")[0]
    assert henderson_section.index("Arabica") < henderson_section.index("Oat Milk")


def test_format_inventory_by_store_handles_single_store():
    products = [
        {
            "store_id": "las-vegas",
            "name": "Vanilla Syrup",
            "quantity": 3,
            "unit": "bottles",
        }
    ]

    rendered = format_inventory_by_store(products)

    assert "=== store_id: las-vegas (Las Vegas, NV) ===" in rendered
    assert "Vanilla Syrup" in rendered
    assert "henderson" not in rendered


def test_format_message_for_log_formats_inventory_tool_results():
    payload = json.dumps(
        [
            {
                "store_id": "henderson",
                "name": "Oat Milk",
                "quantity": 18,
                "unit": "cartons",
            }
        ]
    )

    formatted = format_message_for_log("tool", payload, "list_inventory")

    assert "=== store_id: henderson (Henderson, NV) ===" in formatted
    assert "Oat Milk" in formatted
    assert "product_id" not in formatted


def test_format_message_for_log_leaves_other_messages_unchanged():
    message = '{"product_id": "abc", "quantity": 4}'
    assert format_message_for_log("tool", message, "update_stock") == message
    assert format_message_for_log("agent", "Hello", "") == "Hello"


def test_maybe_print_inventory_table_prints_for_inventory_tools(capsys):
    payload = json.dumps(
        [
            {
                "store_id": "henderson",
                "name": "Oat Milk",
                "quantity": 18,
                "unit": "cartons",
            }
        ]
    )

    printed = maybe_print_inventory_table("list_inventory", payload)
    output = capsys.readouterr().out

    assert printed is True
    assert "store_id: henderson" in output
    assert "Quantity" in output
    assert "Oat Milk" in output


def test_maybe_print_inventory_table_ignores_other_tools(capsys):
    printed = maybe_print_inventory_table("list_stores", '[{"store_id":"henderson"}]')
    output = capsys.readouterr().out

    assert printed is False
    assert output == ""


def test_print_inventory_refresh_prints_formatted_table(capsys):
    payload = json.dumps(
        [
            {
                "store_id": "henderson",
                "name": "Oat Milk",
                "quantity": 10,
                "unit": "cartons",
            }
        ]
    )

    printed = print_inventory_refresh(payload)
    output = capsys.readouterr().out

    assert printed is True
    assert "Oat Milk" in output
    assert "store_id: henderson" in output


def test_should_print_final_response_without_table():
    assert should_print_final_response("All set.", False) is True


def test_should_print_final_response_suppresses_markdown_inventory_list():
    response = "**Henderson Store:**\n- Oat Milk: 18 cartons\n- Arabica: 15 bags\n- Tea: 3 lbs"
    assert should_print_final_response(response, True) is False


def test_should_print_final_response_allows_short_summary_after_table():
    assert should_print_final_response("Las Vegas is lower on lavender syrup.", True) is True


def test_should_print_final_response_suppresses_after_inventory_update():
    assert (
        should_print_final_response(
            "Updated Henderson stock successfully.",
            True,
            inventory_updated=True,
        )
        is False
    )


def test_resolve_turn_inventory_display_refreshes_after_mutations():
    last_view = json.dumps([{"store_id": "henderson", "name": "Tea", "quantity": 1, "unit": "lbs"}])

    payload, is_refresh = resolve_turn_inventory_display(
        1,
        last_view,
        lambda: json.dumps([]),
    )

    assert payload == "[]"
    assert is_refresh is True


def test_resolve_turn_inventory_display_uses_last_view_without_mutations():
    last_view = json.dumps([{"store_id": "henderson", "name": "Tea", "quantity": 1, "unit": "lbs"}])

    payload, is_refresh = resolve_turn_inventory_display(0, last_view, lambda: "[]")

    assert payload == last_view
    assert is_refresh is False


def test_resolve_turn_inventory_display_returns_none_when_no_inventory_tools():
    payload, is_refresh = resolve_turn_inventory_display(0, None, lambda: "[]")

    assert payload is None
    assert is_refresh is False
