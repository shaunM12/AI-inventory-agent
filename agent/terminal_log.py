MESSAGE_PREVIEW_LIMIT = 120


def _truncate(message: str, limit: int = MESSAGE_PREVIEW_LIMIT) -> str:
    if len(message) <= limit:
        return message
    return message[: limit - 3] + "..."


def print_conversation_event(
    actor: str, message: str, tool_call: str, timestamp: str
) -> None:
    from agent.display import format_message_for_log
    from agent.tools import INVENTORY_MUTATION_TOOL_NAMES, INVENTORY_TOOL_NAMES

    if actor == "tool" and tool_call in INVENTORY_MUTATION_TOOL_NAMES | INVENTORY_TOOL_NAMES:
        print(f"[{timestamp}] {actor}")
        print(f"  tool_call: {tool_call}")
        print()
        return

    formatted = format_message_for_log(actor, message, tool_call)
    print(f"[{timestamp}] {actor}")
    print(f"  tool_call: {tool_call or ''}")
    if "\n" in formatted:
        print("  message:")
        for line in formatted.splitlines():
            print(f"    {line}")
    else:
        print(f"  message: {_truncate(formatted)}")
    print()
