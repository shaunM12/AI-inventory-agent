import csv
import os
from datetime import datetime, timezone

from agent import config
from agent.display import format_message_for_log


def make_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _migrate_log_file_if_needed() -> None:
    log_path = config.CONVERSATION_LOG_CSV_PATH
    if not os.path.exists(log_path) or os.path.getsize(log_path) == 0:
        return

    with open(log_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames == config.LOG_COLUMNS:
            return
        if reader.fieldnames != config.LEGACY_LOG_COLUMNS:
            return
        rows = list(reader)

    with open(log_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=config.LOG_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row[column] for column in config.LOG_COLUMNS})


def _ensure_log_file() -> None:
    log_path = config.CONVERSATION_LOG_CSV_PATH
    directory = os.path.dirname(os.path.abspath(log_path))
    if directory:
        os.makedirs(directory, exist_ok=True)

    _migrate_log_file_if_needed()

    if not os.path.exists(log_path) or os.path.getsize(log_path) == 0:
        with open(log_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=config.LOG_COLUMNS)
            writer.writeheader()


def append_conversation_log(
    actor: str, message: str, tool_call: str, timestamp: str
) -> None:
    _ensure_log_file()
    log_path = config.CONVERSATION_LOG_CSV_PATH
    with open(log_path, "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=config.LOG_COLUMNS)
        writer.writerow(
            {
                "actor": actor,
                "tool_call": tool_call,
                "timestamp": timestamp,
                "message": format_message_for_log(actor, message, tool_call),
            }
        )


def log_conversation(actor: str, message: str, tool_call: str = "") -> None:
    append_conversation_log(actor, message, tool_call, make_timestamp())
