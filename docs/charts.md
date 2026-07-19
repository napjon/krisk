# Typed chart reference

`ChartSpec` is the portable chart definition used by Python, REST, and MCP. It forbids
unknown fields, validates required encodings, and rejects executable JavaScript.

## Supported charts

| Kind | Required fields | Useful options |
| --- | --- | --- |
| `bar` | `x` | `y`, `aggregate`, `color`, `stacked`, `annotate` |
| `line` | `x` | `y`, `aggregate`, `color`, `smooth`, `sampling` |
| `area` | `x` | `y`, `aggregate`, `color`, `stacked`, `smooth` |
| `histogram` | `x` | `bins`, `density`, `color` |
| `scatter` | `x`, `y` | `color`, `size` |
| `waterfall` | `x`, `y` | `annotate` |
| `combo` | `x`, `y`, `y2` | `aggregate`, `aggregate_y2` |
| `pie` | `x` | `y`, `aggregate` |
| `doughnut` | `x` | `y`, `aggregate` |
| `sunburst` | `x`, `color` | `y`, `aggregate` |
| `kpi` | `y` | `aggregate`, `number_font_size` |
| `kpi_trend` | `x`, `y` | `aggregate`, `comparison_font_size` |

If `y` is omitted from bar, line, area, pie, or doughnut charts, the default `count`
aggregation counts rows by category.

## Shared fields

```python
from krisk import ChartSpec

spec = ChartSpec(
    kind="bar",
    x="region",
    y="revenue",
    aggregate="sum",  # count, sum, mean, median, min, max, or nunique
    color="segment",
    title="Revenue by region",
    description="Recorded revenue grouped by region and segment",
    theme="light",    # light or dark
    width="100%",
    height=420,
    stacked=True,
    annotate=True,
)
```

`description` is rendered alongside the chart and contributes to the accessible
fallback. `height` is validated between 160 and 2,400 pixels.

## Data inputs

`Chart.from_dataframe` accepts pandas DataFrames and Series, objects with `to_pandas()`,
objects with `execute()` such as many Ibis expressions, and ordinary records that
pandas can convert to a DataFrame.

```python
chart = Chart.from_dataframe(data, spec)
```

The input is copied before compilation. Krisk stores the compiled snapshot data on the
chart so notebook output and `to_html()` remain stable.

## Safe declarative overrides

Use `safe_overrides` for ECharts options that are representable as JSON:

```python
ChartSpec(
    kind="line",
    x="day",
    y="orders",
    aggregate="sum",
    safe_overrides={
        "legend": {"top": 8},
        "grid": {"left": 48, "right": 24},
    },
)
```

Callback-shaped keys such as `formatter`, `renderItem`, and `onClick`, callables, and
strings containing JavaScript function syntax are rejected. This restriction applies
to typed charts accepted from notebooks, REST, and MCP.

## Output formats

In Jupyter, the chart emits a rich MIME bundle with embedded ECharts. In a script:

```python
chart.to_html("chart.html")
```

The HTML is self-contained and includes a collapsible table containing up to the first
100 displayed rows. No Krisk server is required for this static export.

## Legacy plotting API

The original plotting surface remains available:

```python
import krisk.plot as kk

kk.bar(data, "region", y="revenue", how="sum")
kk.line(data, "date", y="revenue", how="sum")
kk.hist(data, "revenue", density=True)
kk.scatter(data, "revenue", y="margin", c="segment")
```

Prefer `ChartSpec` for new MCP-facing or persisted workflows because its schema is
portable, validated, and versioned.
