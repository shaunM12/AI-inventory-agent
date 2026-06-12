import csv
import json

import agent


def test_tool_definitions_include_name_description_and_typed_parameters():
    for tool in agent.TOOL_DEFINITIONS:
        function = tool["function"]
        assert function["name"]
        assert function["description"]
        assert "parameters" in function
        assert function["parameters"]["type"] == "object"


def _tool_call_response(tool_name: str, arguments: dict, call_id: str = "call-1"):
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": call_id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(arguments),
                            },
                        }
                    ],
                }
            }
        ]
    }


def _final_response(content: str):
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": content,
                }
            }
        ]
    }


def test_delivery_message_triggers_positive_update_stock(conversation_log):
    calls = []

    def fake_llm(messages):
        calls.append(messages[-1]["content"])
        if len(calls) == 1:
            return _tool_call_response(
                "update_stock",
                {"product_id": "prod-1", "delta": 30},
            )
        return _final_response("Added 30 units of oat milk.")

    def fake_tool(name, arguments):
        assert name == "update_stock"
        assert arguments["delta"] == 30
        return json.dumps({"product_id": "prod-1", "quantity": 30})

    history = agent.build_initial_history()
    response = agent.run_agent_turn(
        "we just received 30 units of oat milk",
        history,
        llm_client=fake_llm,
        tool_runner=fake_tool,
    )

    assert response == "Added 30 units of oat milk."
    assert len(calls) == 2


def test_sale_message_triggers_negative_update_stock(conversation_log):
    def fake_llm(messages):
        if len(messages) == 2:
            return _tool_call_response(
                "update_stock",
                {"product_id": "prod-2", "delta": -12},
            )
        return _final_response("Recorded a sale of 12 bags of arabica.")

    def fake_tool(name, arguments):
        assert name == "update_stock"
        assert arguments["delta"] == -12
        return json.dumps({"product_id": "prod-2", "quantity": 8})

    history = agent.build_initial_history()
    response = agent.run_agent_turn(
        "we sold 12 bags of arabica today",
        history,
        llm_client=fake_llm,
        tool_runner=fake_tool,
    )

    assert "sale" in response.lower()


def test_low_stock_question_triggers_get_low_stock_alerts(conversation_log):
    def fake_llm(messages):
        if len(messages) == 2:
            return _tool_call_response("get_low_stock_alerts", {})
        return _final_response("Oat milk is running low.")

    def fake_tool(name, arguments):
        assert name == "get_low_stock_alerts"
        return json.dumps([{"name": "Oat Milk", "quantity": 3}])

    history = agent.build_initial_history()
    response = agent.run_agent_turn(
        "what products are running low?",
        history,
        llm_client=fake_llm,
        tool_runner=fake_tool,
    )

    assert "oat milk" in response.lower()


def test_loop_continues_after_tool_execution_and_stops_on_final_response(conversation_log):
    llm_calls = []

    def fake_llm(messages):
        llm_calls.append(len(messages))
        if len(llm_calls) == 1:
            return _tool_call_response("list_inventory", {})
        return _final_response("Inventory loaded.")

    def fake_tool(name, arguments):
        return json.dumps([])

    history = agent.build_initial_history()
    response = agent.run_agent_turn(
        "show inventory",
        history,
        llm_client=fake_llm,
        tool_runner=fake_tool,
    )

    assert response == "Inventory loaded."
    assert len(llm_calls) == 2


def test_message_history_persists_across_multiple_turns(conversation_log):
    def first_llm(_messages):
        return _final_response("First reply.")

    def second_llm(messages):
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "first question"
        assert messages[2]["role"] == "assistant"
        assert messages[3]["role"] == "user"
        assert messages[3]["content"] == "second question"
        return _final_response("Second reply.")

    history = agent.build_initial_history()
    agent.run_agent_turn(
        "first question",
        history,
        llm_client=first_llm,
        tool_runner=lambda *_: "{}",
    )
    agent.run_agent_turn(
        "second question",
        history,
        llm_client=second_llm,
        tool_runner=lambda *_: "{}",
    )


def test_log_rows_append_with_exact_fields(conversation_log):
    def fake_llm(messages):
        if len(messages) == 2:
            return _tool_call_response("get_low_stock_alerts", {})
        return _final_response("All good.")

    agent.run_agent_turn(
        "what products are running low?",
        agent.build_initial_history(),
        llm_client=fake_llm,
        tool_runner=lambda *_: json.dumps([]),
    )

    with conversation_log.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 4
    assert set(rows[0].keys()) == {"actor", "message", "tool_call", "timestamp"}
    assert rows[0]["actor"] == "user"
    assert rows[1]["actor"] == "agent"
    assert rows[1]["tool_call"] == "get_low_stock_alerts"
    assert rows[2]["actor"] == "tool"
    assert rows[3]["actor"] == "agent"


def test_log_rows_format_inventory_as_table(conversation_log):
    inventory = json.dumps(
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

    def fake_llm(messages):
        if len(messages) == 2:
            return _tool_call_response("list_inventory", {})
        return _final_response("Done.")

    agent.run_agent_turn(
        "show inventory",
        agent.build_initial_history(),
        llm_client=fake_llm,
        tool_runner=lambda *_: inventory,
    )

    with conversation_log.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    tool_row = rows[2]
    assert tool_row["actor"] == "tool"
    assert "=== store_id: henderson (Henderson, NV) ===" in tool_row["message"]
    assert "Oat Milk" in tool_row["message"]
    assert "product_id" not in tool_row["message"]
