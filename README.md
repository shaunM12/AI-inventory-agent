# Coffee Shop Inventory API + Agent

A small local inventory system for a coffee shop with **two Nevada stores**:

| Store ID | Location |
|----------|----------|
| `henderson` | Henderson, Nevada |
| `las-vegas` | Las Vegas, Nevada |

The conversational assistant is named **inventory-agent**.

It combines:

- a **FastAPI** backend that persists inventory in `data/products.csv`
- a **plain Python agent** (`agent.py`) that calls the API through a manual LLM tool loop

No LangChain, LlamaIndex, AutoGen, or similar frameworks.

For the full rebuild spec (endpoints, tools, tests, logging rules), see [`context.md`](context.md).

---

## Quick start

### 1. Install

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your own values. **Never commit `.env`.**

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | API key for the OpenAI-compatible LLM client |
| `OPENAI_BASE_URL` | Chat completions base URL |
| `OPENAI_MODEL` | Model name for the agent |
| `API_BASE_URL` | Local inventory API (default `http://127.0.0.1:8000`) |
| `LOW_STOCK_THRESHOLD` | Low-stock alert threshold (default `10`) |
| `STORE_IDS` | Comma-separated store IDs (default `henderson,las-vegas`) |
| `PRODUCTS_CSV_PATH` | Products file (default `data/products.csv`) |
| `CONVERSATION_LOG_CSV_PATH` | Session log (default `data/conversation_log.csv`) |

### 3. Start the API (terminal 1)

The API must be running before the agent starts.

```bash
.venv/bin/uvicorn api.app:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` to explore the API.

### 4. Start the agent (terminal 2)

```bash
.venv/bin/python agent.py
```

Type `exit` or `quit` to end the session.

### 5. Run tests

```bash
.venv/bin/pytest -q
```

---

## Example prompts

- `we just received 30 units of oat milk in Henderson`
- `we sold 12 bags of arabica today in Las Vegas`
- `what products are running low in both stores?`
- `show me the inventory from all stores`
- `show me Henderson inventory`
- `delete oat milk from Henderson`
- `transfer 5 cartons of oat milk from Henderson to Las Vegas`

---

## Agent behavior

- **inventory-agent** runs an Observe → Think → Act → Update loop in plain Python.
- **8 tools** call the API: list stores, list all inventory, get one store's inventory, create product, update stock, delete product, transfer stock, and low-stock alerts.
- Tools live in `agent/tools/` (one module per tool, registered in `registry.py`).
- Inventory is printed as **ASCII tables grouped by store** in the terminal.
- After create/update/delete/transfer, the CLI **reprints the full updated inventory once** at the end of the turn.
- Session events append to `data/conversation_log.csv` (inventory results are stored as formatted tables, not raw JSON).

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/stores` | List configured store IDs |
| `GET` | `/inventory` | List all products (`?store_id=` optional) |
| `GET` | `/stores/{store_id}/inventory` | List one store's products |
| `POST` | `/inventory` | Create a product |
| `PATCH` | `/inventory/{product_id}` | Adjust stock by delta (+ incoming, − outgoing) |
| `DELETE` | `/inventory/{product_id}` | Remove a product row entirely |
| `POST` | `/inventory/transfer` | Move stock between stores |
| `GET` | `/inventory/alerts` | Products below threshold (`?store_id=` optional) |

Stock cannot go below zero. Duplicate product names are allowed across stores but not within the same store.

---

## Data files

### `data/products.csv`

Standard CSV persisted on disk — **survives API and agent restarts**.

Written in readable column order, sorted by store then product name:

```csv
store_id,name,quantity,unit,product_id,created_at,updated_at
henderson,Oat Milk,18,cartons,<uuid>,2026-06-12T20:00:00+00:00,2026-06-12T20:00:00+00:00
```

The repo includes sample boutique inventory (20 products × 2 stores).

### `data/conversation_log.csv`

Append-only session log. Columns:

```csv
actor,tool_call,timestamp,message
```

Contains chat history — treat as private; do not share or commit if it has real session data you care about.

---

## Project structure

```
agent.py                     # CLI entry point
agent/
  api_client.py              # HTTP client for the API
  cli.py                     # terminal loop + table display
  config.py
  conversation_log.py
  display.py                 # inventory table formatting
  llm_client.py
  loop.py                    # agent tool loop
  prompts.py
  terminal_log.py
  tools/                     # one module per tool + registry.py
api/
  app.py                     # FastAPI routes
  config.py
  csv_store.py               # CSV read/write
  inventory_service.py       # business rules
  schemas.py
data/
  products.csv
  conversation_log.csv
tests/
  test_api_inventory.py
  test_agent_loop.py
  test_csv_store.py
  test_display.py
  test_tools_registry.py
  test_conversation_log.py
context.md                   # full reproduction spec
```

---

## Conversation logging

The agent logs every user message, tool call, tool result, and final reply to `data/conversation_log.csv`. It does not store hidden chain-of-thought. Inventory tool output is saved as formatted tables for easier reading in the log file.
