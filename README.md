# Krisk

**Ask questions of live data. Keep the evidence that answered them.**

Krisk is a Python charting library and a local MCP research server. It combines the
notebook workflow from Chartics with the live-server ideas from Flarisk in one package,
without requiring either project as a dependency.

Use Krisk in any of three ways:

| Workflow | What you need | What you get |
| --- | --- | --- |
| Python or Jupyter | Python and a DataFrame | Inline and self-contained HTML charts |
| LLM + MCP | A local Krisk server and named data source | Read-only investigation, saved queries, and charts |
| Living research | A concluded investigation | A point-in-time notebook/report with optional live checks |

Krisk `0.9.0` is an unpublished, local-first beta. Traditional notebook charting does
not require a server, MCP client, PostgreSQL, or even Krisk's internal SQLite database.

## Quick start: a normal notebook

```python
import pandas as pd
from krisk import Chart, ChartSpec

sales = pd.DataFrame(
    {
        "month": ["Jan", "Feb", "Mar"],
        "revenue": [82, 93, 112],
    }
)

chart = Chart.from_dataframe(
    sales,
    ChartSpec(
        kind="area",
        x="month",
        y="revenue",
        aggregate="sum",
        title="Revenue trend",
        description="Monthly recorded revenue",
        smooth=True,
    ),
)

chart  # rich inline output in Jupyter
```

Create a portable HTML file with no CDN dependency:

```python
chart.to_html("revenue.html")
```

Existing Chartics-style calls remain available during the `0.9` preview and planned
`1.x` series:

```python
import krisk.plot as kk

kk.bar(sales, "month", y="revenue", how="sum")
kk.pie(sales, "month", y="revenue", how="sum")
kk.number(sales, "revenue", how="sum")
```

See the [end-to-end tutorial](docs/tutorial.md) and
[typed chart reference](docs/charts.md) for more chart kinds and options.

## Install from this repository

Krisk requires Python 3.11 or newer. Version `1.0.0` has never been published; the
current package version is `0.9.0`.

```bash
git clone https://github.com/napjon/krisk.git
cd krisk
uv sync --extra dev
uv run krisk demo
```

The demo writes `var/krisk/demo.html`.

## Connect an LLM to live data

Krisk never asks an LLM for connection strings. You configure a named source once,
then the LLM can inspect relations and submit bounded, read-only SQL through MCP.

Copy `krisk.toml.example` to `krisk.toml`:

```toml
[sources.local]
kind = "files"
root = "./data"

[sources.analytics]
kind = "postgres"
url_env = "KRISK_ANALYTICS_URL"
```

PostgreSQL is only for an external data source, or for an explicitly shared metadata
deployment. Krisk's own records use SQLite by default.

```bash
export KRISK_ANALYTICS_URL='postgresql://readonly_user:secret@db.example/analytics'
uv run krisk sources validate
uv run krisk serve
```

Local endpoints:

- Dashboard: `http://127.0.0.1:8060/`
- MCP over Streamable HTTP: `http://127.0.0.1:8060/mcp/`
- REST API: `http://127.0.0.1:8060/api/v1`
- Health check: `http://127.0.0.1:8060/health`

For an LLM host that launches stdio MCP servers:

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

The MCP surface supports source discovery, querying, chart creation and refresh,
structured research capture, claim evaluation, and export. See the
[MCP and REST reference](docs/mcp-and-api.md).

## Turn a conversation into living research

The bundled `save-research-notebook` skill guides a compatible LLM through a deliberate
workflow:

1. inspect a named source;
2. run and retain the queries that support the answer;
3. create immutable chart snapshots;
4. separate findings, inference, and limitations;
5. confirm the conclusion with the user;
6. save structured research and optional machine-checkable claims;
7. export a notebook, an HTML report, or both.

```bash
uv run krisk research export RESEARCH_ID
uv run krisk research export RESEARCH_ID --format html
uv run krisk research export RESEARCH_ID --format ipynb
```

Every export preserves the original evidence in the artifact itself. The **Snapshot**
view therefore works offline and cannot silently change. The **Live** view requests
current data from the configured Krisk server, refreshes the chart, and re-evaluates
claims while leaving the saved snapshot untouched.

Exports also contain a data-table fallback, source fingerprints, saved SQL provenance,
claim status at export time, limitations, and reproduction instructions. Read
[Living research](docs/living-research.md) for the full model.

## Local storage

By default, no external infrastructure is used:

```text
var/krisk/
├── krisk.db       # SQLite metadata: queries, charts, and research
├── artifacts/     # content-addressed Parquet chart snapshots
└── exports/       # generated HTML and notebook files
```

Set `KRISK_DATA_DIR` or `KRISK_DATABASE_PATH` to relocate local state. `DATABASE_URL`
is an optional internal metadata override for a deployment that intentionally needs
shared PostgreSQL storage. It is unrelated to named read-only data sources.

## Safety boundaries

Krisk `0.9` is designed for a trusted, single-user machine:

- the server binds to loopback by default and has no remote-user authentication;
- only one `SELECT` or `WITH` statement is accepted per query;
- results and snapshots are capped at 10,000 rows, and snapshots at 5 MiB;
- local file sources expose configured CSV/Parquet relations, not arbitrary paths;
- DuckDB external access and file/network-reading functions are disabled;
- PostgreSQL credentials remain in environment variables and are never exported;
- executable JavaScript is rejected from typed chart overrides.

Use a database-enforced read-only PostgreSQL role as an additional boundary. Do not
expose the `0.9` server to a network without adding authentication and authorization.
See [Security and storage](docs/security-and-storage.md).

## Documentation

- [Documentation index](docs/README.md)
- [End-to-end tutorial](docs/tutorial.md)
- [Typed chart reference](docs/charts.md)
- [MCP and REST reference](docs/mcp-and-api.md)
- [Living research and claims](docs/living-research.md)
- [Security and storage](docs/security-and-storage.md)
- [Release notes](CHANGELOG.md)
- [Implementation review](docs/implementation-review-2026-07-19.md)

### Notebook tours

- [Quick start](notebooks/Intro.ipynb)
- [Declarative visualization](notebooks/declarative-visualization.ipynb)
- [Legends, titles, and toolbox controls](notebooks/legend-title-toolbox.ipynb)
- [Reproducible charts and live refresh](notebooks/resync-reproducible.ipynb)
- [Themes and colors](notebooks/themes-colors.ipynb)
- [Tidy data plotting](notebooks/tidy-plot.ipynb)
- [Waterfall and combination charts](notebooks/waterfall-barline.ipynb)

## Development

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
bun test
uv build
```

The renderer uses Apache ECharts 6.1.0. JavaScript dependencies are managed with Bun
and bundled into the Python wheel. CI tests Python 3.11 through 3.14.

## License

BSD 3-Clause.
