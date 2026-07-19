# End-to-end tutorial

This tutorial begins with ordinary notebook charting, then adds a local file source,
MCP, immutable evidence, and a living research export. Stop after the first section if
all you need is a chart library.

## 1. Install the development checkout

Krisk requires Python 3.11 or newer.

```bash
git clone https://github.com/napjon/krisk.git
cd krisk
uv sync --extra dev
```

Confirm the installed checkout:

```bash
uv run python -c "import krisk; print(krisk.__version__)"
```

The result should be `0.9.0`.

## 2. Create a chart without a server

Run this in Jupyter or save it as a Python script:

```python
import pandas as pd
from krisk import Chart, ChartSpec

sales = pd.DataFrame(
    {
        "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "revenue": [82, 93, 90, 112, 129, 141],
        "channel": ["Direct", "Partner", "Direct", "Partner", "Direct", "Partner"],
    }
)

chart = Chart.from_dataframe(
    sales,
    ChartSpec(
        kind="area",
        x="month",
        y="revenue",
        aggregate="sum",
        color="channel",
        title="Revenue momentum",
        description="Monthly recorded revenue by channel",
        smooth=True,
        height=460,
    ),
)

chart.to_html("revenue.html")
chart
```

The HTML contains ECharts and the snapshot data. It can be opened without Krisk,
Python, a CDN, or network access. It also includes an accessible table fallback.

## 3. Prepare a named local data source

Write the same data to `data/sales.csv`:

```python
from pathlib import Path

Path("data").mkdir(exist_ok=True)
sales.to_csv("data/sales.csv", index=False)
```

Create `krisk.toml`:

```toml
[sources.demo]
kind = "files"
root = "./data"
```

CSV and Parquet filenames become SQL relation names. In this case the relation is
`sales`.

```bash
uv run krisk sources validate
```

Expected output resembles:

```text
demo: ok (1 relations)
```

## 4. Start the local research server

```bash
uv run krisk serve
```

Open `http://127.0.0.1:8060/` to see saved charts and research. The same process serves
REST at `/api/v1` and MCP at `/mcp/`.

Krisk now creates its internal state under `var/krisk/`. This SQLite database stores
metadata only. The CSV remains the source of live values; immutable snapshots are
stored separately as content-addressed Parquet.

## 5. Connect an MCP client

Use Streamable HTTP if the client connects to an already-running server:

```text
http://127.0.0.1:8060/mcp/
```

Use stdio if the client manages the Krisk process:

```json
{
  "mcpServers": {
    "krisk": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/krisk", "run", "krisk", "mcp"]
    }
  }
}
```

The bundled research skill can be located with:

```bash
uv run krisk skill-path
```

Install or expose that directory using the skill mechanism supported by the chosen
LLM client.

## 6. Conduct an investigation

Ask the LLM something concrete, for example:

> Using the `demo` source, investigate whether recorded revenue is at least 600. Show
> the monthly evidence. When we agree on the conclusion, save it as living research.

A sound tool sequence is:

1. `list_sources`
2. `inspect_source(source="demo")`
3. `inspect_source(source="demo", relation="sales")`
4. `run_query` for monthly evidence
5. `run_query` for a one-row claim metric
6. `create_chart` using the monthly query ID
7. discuss findings, limitations, and the conclusion
8. `save_research` only after the user confirms it
9. `export_research`

Suitable SQL for this example:

```sql
SELECT month, channel, sum(revenue) AS revenue
FROM sales
GROUP BY month, channel
ORDER BY month, channel
```

```sql
SELECT sum(revenue) AS value
FROM sales
```

The second query intentionally returns one row with a `value` column, which makes it
suitable for a threshold claim.

## 7. Export the conclusion

The LLM can call `export_research`, or the same saved record can be exported from the
command line:

```bash
uv run krisk research export RESEARCH_ID
```

Choose a single format when needed:

```bash
uv run krisk research export RESEARCH_ID --format html
uv run krisk research export RESEARCH_ID --format ipynb
```

The default output directory is `var/krisk/exports`.

## 8. Verify snapshot versus live behavior

Open the HTML report:

- **Snapshot** renders the values captured during the investigation, even when the
  server is stopped.
- **Live** calls the Krisk server, reruns the saved query, refreshes the chart, and
  evaluates the saved claims.

Now change a value in `data/sales.csv` and reload the Live tab. The live result changes,
but the snapshot and its content hash do not. This is the core guarantee: current data
can challenge a conclusion without rewriting the evidence that produced it.

## 9. Add PostgreSQL only when needed

For an external PostgreSQL source, extend `krisk.toml`:

```toml
[sources.analytics]
kind = "postgres"
url_env = "KRISK_ANALYTICS_URL"
```

```bash
export KRISK_ANALYTICS_URL='postgresql://readonly_user:secret@localhost/analytics'
uv run krisk sources validate
```

Use a database role that can only read the approved schemas. PostgreSQL is not required
for Krisk's local metadata; SQLite remains the default.
