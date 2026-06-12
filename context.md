# Coffee Shop Inventory API + Agent — Reproduction Spec

This document is the source of truth for rebuilding the project from scratch. Hand it to another developer or an AI coding agent along with the repository (or an empty repo) to reproduce the current system.

**Do not put secrets in this file.** Each developer creates their own local `.env` from `.env.example`.

---

## Summary

A small local inventory system with two cooperating parts:

1. **FastAPI backend** (`api/`) — persists inventory in `data/products.csv`
2. **Plain Python agent** (`agent/` + root `agent.py`) — talks to the API through a manual LLM tool loop (no LangChain, LlamaIndex, AutoGen, or similar)

The conversational assistant is named **inventory-agent**.

### Stores (Nevada)

| Store ID | Location |
|----------|----------|
| `henderson` | Henderson, Nevada |
| `las-vegas` | Las Vegas, Nevada |

Each store has its own rows in the same CSV. The API and agent support one store or both.

### Example owner prompts

- "we just received 30 units of oat milk in Henderson"
- "we sold 12 bags of arabica today in Las Vegas"
- "what products are running low in both stores?"
- "show me the inventory from all stores"
- "delete oat milk from Henderson"
- "transfer 5 cartons of oat milk from Henderson to Las Vegas"

The system should feel like a conversation, not a form.

---

## Quick Start (Reproduction Steps)

### 1. Prerequisites

- Python 3.12+ recommended
- An OpenAI-compatible LLM API key (OpenAI, LiteLLM proxy, etc.)

### 2. Install

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` locally with **your own** values. Never commit `.env`.

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | API key for the LLM provider |
| `OPENAI_BASE_URL` | Chat completions base URL (e.g. `https://api.openai.com/v1`) |
| `OPENAI_MODEL` | Model name (e.g. `gpt-4o-mini`) |
| `API_BASE_URL` | Local inventory API (default `http://127.0.0.1:8000`) |
| `LOW_STOCK_THRESHOLD` | Alert threshold (default `10`) |
| `STORE_IDS` | Comma-separated store IDs (default `henderson,las-vegas`) |
| `PRODUCTS_CSV_PATH` | Path to products file (default `data/products.csv`) |
| `CONVERSATION_LOG_CSV_PATH` | Path to conversation log (default `data/conversation_log.csv`) |

Both `api/config.py` and `agent/config.py` call `load_dotenv(override=True)` so `.env` wins over shell variables.

### 4. Seed inventory (optional)

Provide a starter `data/products.csv` with boutique coffee inventory: **20 products × 2 stores = 40 rows**. See [Products CSV](#products-csv) for format. An empty file gets a header on first API write.

### 5. Start the API (terminal 1)

```bash
.venv/bin/uvicorn api.app:app --reload --host 127.0.0.1 --port 8000
```

Verify: `http://127.0.0.1:8000/docs`

### 6. Start the agent (terminal 2)

The API **must** be running first.

```bash
.venv/bin/python agent.py
```

Type `exit` or `quit` to end the session.

### 7. Run tests

```bash
.venv/bin/pytest -q
```

Expect **54+ passing tests** across API, agent, CSV store, display, tools registry, and conversation log modules.

---

## Project Structure

```
project/
  README.md
  context.md                 # this file
  requirements.txt
  pytest.ini
  .env.example               # tracked — placeholders only
  .gitignore                 # must ignore .env
  agent.py                   # thin CLI entry point
  agent/
    __init__.py
    api_client.py            # HTTP client for inventory API
    cli.py                   # terminal loop + display orchestration
    config.py
    conversation_log.py      # append-only CSV logging
    display.py               # inventory table formatting + print rules
    llm_client.py            # OpenAI-compatible chat completions
    loop.py                  # Observe → Think → Act → Update loop
    prompts.py               # SYSTEM_PROMPT for inventory-agent
    terminal_log.py          # compact terminal event preview
    tools/
      __init__.py
      base.py                # Tool dataclass
      registry.py            # TOOL_REGISTRY, run_tool(), tool name sets
      list_stores.py
      get_store_inventory.py
      list_inventory.py
      create_product.py
      update_stock.py
      delete_product.py
      transfer_stock.py
      get_low_stock_alerts.py
  api/
    __init__.py
    app.py                   # FastAPI routes + exception handlers
    config.py
    schemas.py
    inventory_service.py     # business rules
    csv_store.py             # atomic CSV read/write
  data/
    products.csv             # inventory persistence (runtime)
    conversation_log.csv     # agent session log (runtime, append-only)
  tests/
    conftest.py
    test_api_inventory.py
    test_agent_loop.py
    test_csv_store.py
    test_display.py
    test_tools_registry.py
    test_conversation_log.py
```

### Organization rules

- Root `agent.py` is only the entry point; logic lives under `agent/`.
- All FastAPI code lives under `api/`.
- Runtime CSV files live only under `data/`.
- Route wiring in `api/app.py`; business rules in `api/inventory_service.py`; persistence in `api/csv_store.py`.
- Agent tools: one module per tool; register in `agent/tools/registry.py`.
- `.env` is gitignored; `.env.example` is tracked with placeholders only.

---

## Products CSV

Standard comma-separated CSV. Logical columns (all required on each row):

- `product_id` — UUID, generated on create
- `store_id` — must match `STORE_IDS`
- `name` — unique per store (case-insensitive)
- `quantity` — non-negative integer
- `unit` — free text (e.g. `bags`, `cartons`, `boxes`)
- `created_at` — ISO 8601 UTC
- `updated_at` — ISO 8601 UTC

### On-disk column order (readable)

Written by `api/csv_store.py` in this order for easier reading:

```csv
store_id,name,quantity,unit,product_id,created_at,updated_at
henderson,Oat Milk,18,cartons,<uuid>,2026-06-12T20:00:00+00:00,2026-06-12T20:00:00+00:00
```

Rows are sorted by `store_id`, then product name (case-insensitive), then `product_id`.

### Persistence rules

- Atomic writes via temp file + `os.replace`
- `read_products()` accepts legacy formats (old column order, flat pipe tables, grouped text) for migration; `write_products()` always emits readable CSV
- Duplicate product names forbidden within the same store; allowed across stores

---

## API Specification

Base URL: `API_BASE_URL` (default `http://127.0.0.1:8000`)

All error responses use JSON: `{"detail": "<message>"}`

### `GET /stores`

Returns configured store IDs.

- **200** — `[{"store_id": "henderson"}, {"store_id": "las-vegas"}]`

### `GET /inventory`

Returns all products. Optional query: `store_id` filters to one store.

- **200** — list of products
- **404** — invalid `store_id`
- **500** — read/persistence failure

### `GET /stores/{store_id}/inventory`

Returns products for one store (same as `GET /inventory?store_id=`).

- **200** / **404** / **500** — same as above

### `POST /inventory`

Create a product.

Request body:

```json
{
  "store_id": "henderson",
  "name": "Oat Milk",
  "quantity": 30,
  "unit": "cartons"
}
```

- **201** — created product
- **400** — blank name/unit, negative quantity, etc.
- **404** — invalid store
- **409** — duplicate name in same store
- **500** — write failure

### `PATCH /inventory/{product_id}`

Adjust stock by delta (integer, non-zero).

```json
{ "delta": 5 }
```

Positive = incoming; negative = outgoing.

- **200** — updated product
- **400** — delta is zero
- **404** — product not found
- **409** — would go below zero
- **500** — write failure

### `DELETE /inventory/{product_id}`

Permanently removes the product row.

- **200** — returns deleted product
- **404** — not found
- **500** — write failure

### `POST /inventory/transfer`

Move stock from the source product's store to another store.

```json
{
  "product_id": "<source-product-uuid>",
  "to_store_id": "las-vegas",
  "quantity": 5
}
```

Behavior:

- Decreases source quantity by `quantity`
- If destination has same product name (case-insensitive) and same unit → add quantity
- Else → create new product at destination
- Rejects same-store transfer, insufficient source stock, unit mismatch at destination

- **200** — `TransferResult` with source and destination products
- **400** — validation errors
- **404** — product or store not found
- **409** — insufficient stock
- **500** — write failure

### `GET /inventory/alerts`

Products with `quantity < LOW_STOCK_THRESHOLD` (default 10). Optional `store_id` filter.

- **200** / **404** / **500**

---

## Agent Architecture

### No frameworks

Implement manually in plain Python. Do **not** use LangChain, LlamaIndex, AutoGen, or similar.

### Loop (`agent/loop.py`)

1. **Observe** — read user input; append to message history
2. **Think** — send history + tool definitions to LLM
3. **Act** — run selected tool via `agent/tools/registry.run_tool()`
4. **Update** — append tool result to history
5. Repeat until LLM returns a final message with no pending tool calls

### LLM client (`agent/llm_client.py`)

- OpenAI-compatible `POST {OPENAI_BASE_URL}/chat/completions`
- Sends all `TOOL_DEFINITIONS` with `tool_choice: auto`
- Requires `OPENAI_API_KEY`

### Tool registry (`agent/tools/`)

Each tool module exports:

- `NAME` — tool name string
- `DEFINITION` — OpenAI function schema dict
- `run(arguments) -> Any` — calls `agent/api_client.py`
- `TOOL = Tool(...)` — with optional flags:
  - `inventory_display=True` — result is an inventory list shown as a table
  - `inventory_mutation=True` — changes inventory; triggers end-of-turn refresh

`registry.py` builds `TOOL_DEFINITIONS`, `TOOL_REGISTRY`, `INVENTORY_TOOL_NAMES`, `INVENTORY_MUTATION_TOOL_NAMES`, and `run_tool()`.

### Agent tools (8 total)

| Tool | API call | Parameters | Flags |
|------|----------|------------|-------|
| `list_stores` | `GET /stores` | none | |
| `get_store_inventory` | `GET /stores/{id}/inventory` | `store_id` (required) | display |
| `list_inventory` | `GET /inventory` | none (all stores) | display |
| `create_product` | `POST /inventory` | `store_id`, `name`, `quantity`, `unit` | mutation |
| `update_stock` | `PATCH /inventory/{id}` | `product_id`, `delta` | mutation |
| `delete_product` | `DELETE /inventory/{id}` | `product_id` | mutation |
| `transfer_stock` | `POST /inventory/transfer` | `product_id`, `to_store_id`, `quantity` | mutation |
| `get_low_stock_alerts` | `GET /inventory/alerts` | `store_id` (optional) | display |

**Important agent rules** (also in `agent/prompts.py`):

- Use `delete_product` to remove a product entirely — never zero out stock with `update_stock` as a substitute
- Use `get_store_inventory` when one store is mentioned; use `list_inventory` for all stores
- Before update/delete/transfer, list inventory when needed to resolve `product_id` from name
- Ask clarifying questions when ambiguous; do not guess

---

## Terminal UX (`agent/cli.py` + `agent/display.py`)

### Inventory tables

When inventory tools return product lists, print ASCII tables grouped by store:

```
=== store_id: henderson (Henderson, NV) ===
Name                         Quantity  Unit
Oat Milk                           18  cartons
...
```

### End-of-turn display (one table max)

After all tool calls in a turn complete:

- **View only** (`list_inventory`, `get_store_inventory`, `get_low_stock_alerts`) → print table once from tool result
- **Any mutation** (`create_product`, `update_stock`, `delete_product`, `transfer_stock`) → fetch fresh inventory from API and print once
- If both mutation and view tools run in one turn → only the post-mutation refresh prints (no duplicate)

### Agent message suppression

- After an inventory **update**, suppress the agent's final reply when a table was printed (avoid duplicating the table in prose)
- After view-only requests, allow a short non-list summary
- Suppress markdown bullet lists when a table was already printed

### Terminal log preview (`agent/terminal_log.py`)

For inventory and mutation tool events, print only timestamp + actor + tool name (not full JSON/table) to avoid duplicate output. Full content still goes to `conversation_log.csv`.

---

## Conversation Log (`data/conversation_log.csv`)

Append-only. **Do not share this file** — it contains session history.

### Column order

```csv
actor,tool_call,timestamp,message
```

(Legacy files with `actor,message,tool_call,timestamp` auto-migrate on next append.)

### Field meanings

| Field | Values |
|-------|--------|
| `actor` | `user`, `agent`, or `tool` |
| `tool_call` | tool name, or empty |
| `timestamp` | ISO 8601 UTC |
| `message` | event text or tool result |

### Formatting rules

- Log every user message, agent tool-call intent, tool result, and final agent reply
- For inventory tool results, store **formatted tables** in `message` (via `format_message_for_log()`), not raw JSON
- After mutation refresh, append an extra `tool` row with `tool_call=list_inventory` and the refreshed table
- Never log hidden chain-of-thought

---

## System Prompt (`agent/prompts.py`)

Key behaviors baked into `SYSTEM_PROMPT`:

- Friendly **inventory-agent** persona for two Nevada stores
- Tool selection rules (delete vs update, single store vs all stores, transfer workflow)
- CLI prints structured tables; agent should not repeat item lists in final messages
- After mutations, CLI auto-reprints inventory — agent gives at most 1–2 sentences of confirmation

---

## Dependencies (`requirements.txt`)

```
fastapi>=0.115.0
uvicorn>=0.32.0
httpx>=0.27.0
python-dotenv>=1.0.0
pytest>=8.0.0
```

---

## Test Plan

### API (`tests/test_api_inventory.py`)

- `GET /stores` returns both stores
- `GET /inventory` returns all rows; `?store_id=` filters
- `GET /stores/{store_id}/inventory` returns one store
- `POST /inventory` creates product (201)
- `PATCH /inventory/{id}` positive/negative delta; rejects below zero
- `DELETE /inventory/{id}` removes row
- `POST /inventory/transfer` moves/merges stock; rejects invalid cases
- `GET /inventory/alerts` threshold + store filter
- Invalid requests return descriptive 4xx

### Agent loop (`tests/test_agent_loop.py`)

- Tool definitions have name, description, typed parameters
- Delivery/sale phrasing triggers `update_stock` (+/- delta)
- Low-stock questions trigger `get_low_stock_alerts`
- Loop continues after tools; stops on final response
- Message history persists across turns
- Log rows append with correct fields; inventory logged as formatted table

### CSV store (`tests/test_csv_store.py`)

- Writes readable CSV column order; sorts rows
- Reads legacy CSV and old table formats
- Round-trip read/write preserves data

### Display (`tests/test_display.py`)

- Table formatting by store
- End-of-turn display resolution (mutation vs view)
- Final response suppression rules

### Tools registry (`tests/test_tools_registry.py`)

- Unique tool names
- `INVENTORY_TOOL_NAMES` / `INVENTORY_MUTATION_TOOL_NAMES` match tool flags

### Conversation log (`tests/test_conversation_log.py`)

- New files use reordered columns
- Legacy log files migrate automatically

---

## Manual Acceptance Scenarios

1. "we just received 30 units of oat milk in Henderson" → stock increases; inventory table reprints
2. "we sold 12 bags of arabica today in Las Vegas" → stock decreases; table reprints
3. "what products are running low?" → alerts table; short agent summary
4. "show me the inventory from all stores" → both stores in table; no duplicate bullet list
5. "show me Henderson inventory" → single-store table via `get_store_inventory`
6. "delete almost milk from both stores" → `delete_product` twice; rows removed; table reprints
7. "transfer 3 oat milk from Henderson to Las Vegas" → transfer succeeds; table reprints
8. Several back-to-back prompts retain session context

---

## What Not to Share

When giving this project or `context.md` to someone else, **exclude**:

- `.env` (real API keys and provider URLs)
- `data/conversation_log.csv` (private chat history)
- Any credentials or tokens

**Safe to share:**

- Source code
- `context.md`
- `.env.example`
- `data/products.csv` (inventory data only — no secrets)

---

## Assumptions

- Runs locally on one machine; API and agent are separate processes
- LLM client is OpenAI-compatible; configured entirely via environment variables
- `products.csv` is the MVP persistence layer (not a production database)
- File layout favors clarity over heavy abstraction
- Both stores are in Nevada; IDs map to Henderson and Las Vegas
