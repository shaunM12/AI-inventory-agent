import pytest

import agent.config


@pytest.fixture()
def conversation_log(tmp_path, monkeypatch):
    log_path = tmp_path / "conversation_log.csv"
    monkeypatch.setattr(agent.config, "CONVERSATION_LOG_CSV_PATH", str(log_path))
    return log_path
