import csv

import agent.config
from agent.conversation_log import append_conversation_log, make_timestamp


def test_new_log_file_uses_reordered_columns(tmp_path, monkeypatch):
    log_path = tmp_path / "conversation_log.csv"
    monkeypatch.setattr(agent.config, "CONVERSATION_LOG_CSV_PATH", str(log_path))

    append_conversation_log("user", "hello", "", make_timestamp())

    with log_path.open(newline="", encoding="utf-8") as handle:
        header = handle.readline().strip()

    assert header == "actor,tool_call,timestamp,message"


def test_legacy_log_file_is_migrated(tmp_path, monkeypatch):
    log_path = tmp_path / "conversation_log.csv"
    monkeypatch.setattr(agent.config, "CONVERSATION_LOG_CSV_PATH", str(log_path))

    with log_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=agent.config.LEGACY_LOG_COLUMNS)
        writer.writeheader()
        writer.writerow(
            {
                "actor": "user",
                "message": "hello",
                "tool_call": "",
                "timestamp": "2026-06-12T10:00:00+00:00",
            }
        )

    append_conversation_log("agent", "hi back", "", make_timestamp())

    with log_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert list(rows[0].keys()) == agent.config.LOG_COLUMNS
    assert rows[0]["message"] == "hello"
    assert rows[0]["actor"] == "user"


def test_inventory_tool_row_puts_metadata_before_message(tmp_path, monkeypatch):
    log_path = tmp_path / "conversation_log.csv"
    monkeypatch.setattr(agent.config, "CONVERSATION_LOG_CSV_PATH", str(log_path))

    table = "=== store_id: henderson (Henderson, NV) ===\nOat Milk  18  cartons"
    append_conversation_log("tool", table, "list_inventory", make_timestamp())

    raw = log_path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    assert lines[0] == "actor,tool_call,timestamp,message"
    assert lines[1].startswith("tool,list_inventory,")
    assert "=== store_id: henderson" in lines[1] or lines[2].startswith("=== store_id")
