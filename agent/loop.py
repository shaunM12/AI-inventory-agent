import json
from typing import Any, Callable

from agent.conversation_log import log_conversation
from agent.llm_client import call_llm, extract_assistant_message
from agent.prompts import SYSTEM_PROMPT
from agent.tools import run_tool


def run_agent_turn(
    user_input: str,
    message_history: list[dict[str, Any]],
    *,
    llm_client: Callable[[list[dict[str, Any]]], dict[str, Any]] = call_llm,
    tool_runner: Callable[[str, dict[str, Any]], str] = run_tool,
    logger: Callable[[str, str, str], None] = log_conversation,
    on_tool_result: Callable[[str, str], None] | None = None,
) -> str:
    message_history.append({"role": "user", "content": user_input})
    logger("user", user_input)

    while True:
        completion = llm_client(message_history)
        assistant_message = extract_assistant_message(completion)
        message_history.append(assistant_message)

        tool_calls = assistant_message.get("tool_calls") or []
        if not tool_calls:
            final_response = assistant_message.get("content") or ""
            logger("agent", final_response)
            return final_response

        for tool_call in tool_calls:
            function = tool_call["function"]
            tool_name = function["name"]
            arguments = json.loads(function.get("arguments") or "{}")
            logger("agent", json.dumps(arguments), tool_name)

            tool_result = tool_runner(tool_name, arguments)
            logger("tool", tool_result, tool_name)
            if on_tool_result:
                on_tool_result(tool_name, tool_result)

            message_history.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result,
                }
            )


def build_initial_history() -> list[dict[str, Any]]:
    return [{"role": "system", "content": SYSTEM_PROMPT}]
