import os

from dotenv import load_dotenv

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
CONVERSATION_LOG_CSV_PATH = os.getenv(
    "CONVERSATION_LOG_CSV_PATH", "data/conversation_log.csv"
)

LOG_COLUMNS = ["actor", "tool_call", "timestamp", "message"]
LEGACY_LOG_COLUMNS = ["actor", "message", "tool_call", "timestamp"]
