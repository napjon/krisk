# MCP and REST reference

The REST API and MCP server are thin interfaces over the same `KriskService`. Records
created through one interface are immediately visible through the others.

## Start the server

```bash
uv run krisk serve
```

The default bind is `127.0.0.1:8060`. Remote binding is intentionally rejected unless
`KRISK_ALLOW_INSECURE_REMOTE_BIND=1` is set. That escape hatch does not add
authentication; it only acknowledges the risk.

## MCP transports

| Transport | Entry point | Use case |
| --- | --- | --- |
| Streamable HTTP | `http://127.0.0.1:8060/mcp/` | A client connects to the running server |
| stdio | `uv run krisk mcp` | The LLM host launches and owns the process |

Both transports expose the same tools, resources, and methodology prompt.

## MCP tools

| Tool | Purpose |
| --- | --- |
| `list_sources` | Return source name, adapter kind, health, and fingerprint |
| `inspect_source` | List relations or columns for one relation |
| `run_query` | Execute bounded read-only SQL and save its provenance |
| `create_chart` | Compile a typed chart and save an immutable snapshot |
| `refresh_chart` | Rerun the saved query without changing the snapshot |
| `save_research` | Save confirmed methodology, evidence, conclusion, and claims |
| `evaluate_research` | Rerun all machine-checkable claims |
| `export_research` | Write HTML, Jupyter, or both |
| `export_saved_research` | Compatibility alias for `export_research` |

`run_query` returns a preview and stable query ID. The complete bounded result is
executed again when a chart is created or refreshed; it is not accepted from the LLM as
untrusted chart data.

## MCP resources and prompt

```text
krisk://research/{research_id}
krisk://research/{research_id}/export-manifest
krisk://chart/{chart_id}/snapshot
krisk://chart/{chart_id}/current
```

The `research_methodology(question)` prompt tells an agent to inspect before querying,
retain evidence IDs, distinguish observation from inference, record limitations, and
wait for confirmation before saving research.

## REST endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Server status and configured-source count |
| `GET` | `/api/v1/sources` | List named sources |
| `GET` | `/api/v1/sources/{source}` | List or inspect relations |
| `POST` | `/api/v1/queries` | Run and save a query |
| `POST` | `/api/v1/charts` | Create a chart snapshot |
| `GET` | `/api/v1/charts` | List charts |
| `GET` | `/api/v1/charts/{id}` | Get a saved chart and snapshot metadata |
| `GET` | `/api/v1/charts/{id}/current` | Refresh current data |
| `POST` | `/api/v1/research` | Save structured research |
| `GET` | `/api/v1/research` | List research records |
| `GET` | `/api/v1/research/{id}` | Get one research record |
| `GET` | `/api/v1/research/{id}/evaluate` | Evaluate its claims |
| `POST` | `/api/v1/research/{id}/export` | Export selected formats |

Human-readable views are available at `/`, `/charts/{id}`, and `/research/{id}`.
`/simpleRequestServer` retains the original Flarisk demonstration payload for
compatibility and should not be used by new integrations.

## REST example

Run a query:

```bash
curl -X POST http://127.0.0.1:8060/api/v1/queries \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "demo",
    "sql": "SELECT month, sum(revenue) AS revenue FROM sales GROUP BY month"
  }'
```

Create a chart using the returned query ID:

```bash
curl -X POST http://127.0.0.1:8060/api/v1/charts \
  -H 'Content-Type: application/json' \
  -d '{
    "query_id": "QUERY_ID",
    "spec": {
      "kind": "bar",
      "x": "month",
      "y": "revenue",
      "aggregate": "sum",
      "title": "Revenue by month"
    }
  }'
```

## Error behavior

- invalid or unsafe SQL returns HTTP 400 or an MCP tool error;
- missing IDs return HTTP 404;
- a live refresh can fail when its named source is unavailable, but the saved snapshot
  remains readable;
- claim evaluation reports `unknown` when its source or expected result shape is
  unavailable instead of rewriting or guessing the result.
