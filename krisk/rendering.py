"""Self-contained notebook and HTML rendering."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from krisk.specs import as_dataframe
from krisk.util import join_current_dir


def option_json(option: dict[str, Any]) -> str:
    return json.dumps(option, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def chart_fragment(
    option: dict[str, Any],
    chart_id: str,
    height: int = 420,
    description: str | None = None,
    table_data: Any = None,
) -> str:
    summary = html.escape(description or "Interactive chart")
    fallback = table_fallback(table_data) if table_data is not None else ""
    return f"""
<section class="krisk-chart" aria-label="{summary}">
  <div id="krisk-{chart_id}" style="width:100%;height:{height}px"></div>
  <p class="krisk-fallback">{summary}</p>
  {fallback}
</section>
<script>
(() => {{
  const el = document.getElementById("krisk-{chart_id}");
  if (!el || typeof echarts === "undefined") return;
  const chart = echarts.init(el);
  chart.setOption({option_json(option)});
  new ResizeObserver(() => chart.resize()).observe(el);
}})();
</script>"""


def standalone_html(
    option: dict[str, Any],
    chart_id: str,
    title: str,
    height: int = 420,
    description: str | None = None,
    live_url: str | None = None,
    table_data: Any = None,
) -> str:
    echarts_source = (
        Path(join_current_dir("static/echarts.min.js"))
        .read_text(encoding="utf-8")
        .replace("</script>", "<\\/script>")
    )
    live_script = Path(join_current_dir("static/krisk-live.js")).read_text(encoding="utf-8")
    live_attr = html.escape(live_url or "", quote=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(title or "Krisk chart")}</title>
  <style>
    :root {{ color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
    body {{ max-width: 1100px; margin: 2rem auto; padding: 0 1rem; background:#f8fafc; color:#172033; }}
    .tabs {{ display:flex; gap:.5rem; margin-bottom:1rem; }}
    button {{ border:1px solid #cbd5e1; border-radius:.55rem; padding:.55rem .9rem; background:#f8fafc; cursor:pointer; }}
    button[aria-selected="true"] {{ background:#172554; color:white; }}
    #static-panel,#live-panel {{ background:white; border:1px solid #e2e8f0; border-radius:1rem; padding:1rem; box-shadow:0 12px 35px #0f172a0d; }}
    .status {{ min-height:1.5rem; color:#475569; }}
    details {{ margin-top:1rem; }} table {{ border-collapse:collapse;width:100%;font-size:.9rem; }} th,td {{ border-bottom:1px solid #e2e8f0;padding:.5rem;text-align:left; }}
    [hidden] {{ display:none !important; }}
  </style>
  <script>{echarts_source}</script>
</head>
<body data-live-url="{live_attr}">
  <h1>{html.escape(title or "Krisk chart")}</h1>
  <div class="tabs" role="tablist" aria-label="Chart data mode">
    <button id="static-tab" role="tab" aria-selected="true" aria-controls="static-panel">Snapshot</button>
    <button id="live-tab" role="tab" aria-selected="false" aria-controls="live-panel" {"disabled" if not live_url else ""}>Live</button>
  </div>
  <section id="static-panel" role="tabpanel" aria-labelledby="static-tab">
    {chart_fragment(option, chart_id, height, description, table_data)}
  </section>
  <section id="live-panel" role="tabpanel" aria-labelledby="live-tab" hidden>
    <div id="live-chart" style="width:100%;height:{height}px"></div>
    <button id="refresh-live" type="button">Refresh current data</button>
    <p id="live-status" class="status" aria-live="polite"></p>
    <div id="claim-status"></div>
  </section>
  <script>{live_script}</script>
</body>
</html>"""


def table_fallback(data: Any, max_rows: int = 100) -> str:
    frame = as_dataframe(data)
    table = frame.head(max_rows).to_html(index=False, border=0, escape=True)
    note = (
        f"<p>Showing the first {max_rows:,} of {len(frame):,} rows.</p>"
        if len(frame) > max_rows
        else ""
    )
    return f"<details><summary>View chart data as a table</summary>{note}{table}</details>"
