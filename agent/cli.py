import json

from agent import api_client, config
from agent.conversation_log import append_conversation_log, make_timestamp
from agent.display import (
    maybe_print_inventory_table,
    print_inventory_refresh,
    resolve_turn_inventory_display,
    should_print_final_response,
)
from agent.loop import build_initial_history, run_agent_turn
from agent.terminal_log import print_conversation_event
from agent.tools import INVENTORY_MUTATION_TOOL_NAMES, INVENTORY_TOOL_NAMES


def cli_logger(actor: str, message: str, tool_call: str = "") -> None:
    timestamp = make_timestamp()
    append_conversation_log(actor, message, tool_call, timestamp)
    print_conversation_event(actor, message, tool_call, timestamp)


def main() -> int:
    print("Coffee Shop Inventory Agent")
    print("Type 'exit' or 'quit' to end the session.")
    print(f"API base URL: {config.API_BASE_URL}")
    print()

    message_history = build_initial_history()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break

        table_printed = False
        mutations_this_turn = 0
        last_inventory_json: str | None = None

        def on_tool_result(tool_name: str, tool_result: str) -> None:
            nonlocal mutations_this_turn, last_inventory_json
            if tool_name in INVENTORY_MUTATION_TOOL_NAMES:
                mutations_this_turn += 1
                return
            if tool_name in INVENTORY_TOOL_NAMES:
                last_inventory_json = tool_result

        try:
            response = run_agent_turn(
                user_input,
                message_history,
                logger=cli_logger,
                on_tool_result=on_tool_result,
            )
        except Exception as exc:
            response = f"Sorry, something went wrong: {exc}"
            cli_logger("agent", response)
            table_printed = False
            mutations_this_turn = 0
        else:
            inventory_json, is_mutation_refresh = resolve_turn_inventory_display(
                mutations_this_turn,
                last_inventory_json,
                lambda: json.dumps(api_client.list_inventory(), default=str),
            )
            if inventory_json and print_inventory_refresh(inventory_json):
                table_printed = True
                if is_mutation_refresh:
                    append_conversation_log(
                        "tool",
                        inventory_json,
                        "list_inventory",
                        make_timestamp(),
                    )

        if should_print_final_response(
            response,
            table_printed,
            inventory_updated=mutations_this_turn > 0,
        ):
            print(f"inventory-agent: {response}")
        print()

    return 0
