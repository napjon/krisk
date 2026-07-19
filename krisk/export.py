"""Deterministic living-research notebook and HTML export."""

from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Any, Literal

import nbformat
import pandas as pd

from krisk.rendering import option_json, table_fallback
from krisk.service import KriskService
from krisk.util import join_current_dir


def export_research(
    service: KriskService,
    research_id: str,
    output_dir: Path,
    base_url: str = "http://127.0.0.1:8060",
    output_format: Literal["html", "ipynb", "both"] = "both",
) -> dict[str, str]:
    research = service.get_research(research_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    charts = [service.get_chart(chart_id) for chart_id in research["chart_ids"]]
    queries = _research_queries(service, research)
    claims = service.evaluate_research(research_id)
    html_path = output_dir / f"research-{research_id}.html"
    notebook_path = output_dir / f"research-{research_id}.ipynb"
    paths: dict[str, str] = {}
    if output_format in {"html", "both"}:
        html_path.write_text(
            _research_html(research, charts, queries, claims, base_url),
            encoding="utf-8",
        )
        paths["html"] = str(html_path)
    if output_format in {"ipynb", "both"}:
        nbformat.write(_research_notebook(service, research, charts, base_url), notebook_path)
        paths["ipynb"] = str(notebook_path)
    return paths


def render_research_html(
    service: KriskService,
    research_id: str,
    base_url: str = "",
) -> str:
    """Render a saved research record for the server without writing a file."""
    research = service.get_research(research_id)
    charts = [service.get_chart(chart_id) for chart_id in research["chart_ids"]]
    return _research_html(
        research,
        charts,
        _research_queries(service, research),
        service.evaluate_research(research_id),
        base_url,
    )


def _research_html(
    research: dict[str, Any],
    charts: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    base_url: str,
) -> str:
    echarts = (
        Path(join_current_dir("static/echarts.min.js"))
        .read_text(encoding="utf-8")
        .replace("</script>", "<\\/script>")
    )
    chart_sections = "\n".join(_living_card(chart, base_url) for chart in charts)
    methods = "".join(f"<li>{html.escape(item)}</li>" for item in research["methodology"])
    findings = "".join(f"<li>{html.escape(item)}</li>" for item in research["findings"])
    limitations = "".join(f"<li>{html.escape(item)}</li>" for item in research["limitations"])
    provenance = (
        "".join(
            f"<details><summary>{html.escape(query['source'])} · query {html.escape(query['id'])}</summary>"
            f"<p>Source fingerprint: <code>{html.escape(query.get('source_fingerprint') or 'unavailable')}</code></p>"
            f"<pre><code>{html.escape(query['sql'])}</code></pre></details>"
            for query in queries
        )
        or "<p>No query provenance was recorded.</p>"
    )
    claim_items = (
        "".join(
            f'<li class="claim-{html.escape(claim["status"])}"><strong>{html.escape(claim["status"].upper())}</strong> '
            f"{html.escape(claim['label'])} — {html.escape(claim['message'])}</li>"
            for claim in claims
        )
        or "<li>No executable claims recorded.</li>"
    )
    hypothesis = (
        f"<h2>Hypothesis</h2><p>{html.escape(research['hypothesis'])}</p>"
        if research.get("hypothesis")
        else ""
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(research["question"])}</title>
<style>{_research_css()}</style><script>{echarts}</script></head>
<body><main>
<p class="eyebrow">Krisk living research</p>
<h1>{html.escape(research["question"])}</h1>
<p class="meta">Captured {html.escape(research["created_at"])}</p>
{hypothesis}
<h2>Methodology</h2><ol>{methods}</ol>
<h2>Evidence</h2>{chart_sections}
<h2>Sources and provenance</h2>{provenance}
<h2>Findings</h2><ul>{findings}</ul>
<h2>Conclusion</h2><p class="conclusion">{html.escape(research["conclusion"])}</p>
<h2>Claim status at export</h2><ul>{claim_items}</ul>
<h2>Limitations</h2><ul>{limitations or "<li>None recorded.</li>"}</ul>
<h2>Reproduce</h2><ol><li>Connect the named sources shown above.</li><li>Run the recorded read-only SQL.</li><li>Compare results with the immutable chart snapshot, then use Live to evaluate current data.</li></ol>
</main><script>{_research_js()}</script></body></html>"""


def _research_queries(service: KriskService, research: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        query
        for query_id in research["query_ids"]
        if (query := service.repository.get("query", query_id)) is not None
    ]


def _living_card(chart: dict[str, Any], base_url: str) -> str:
    chart_id = chart["id"]
    spec = chart["spec"]
    captured = chart["snapshot"]["captured_at"]
    live_url = f"{base_url.rstrip('/')}/api/v1/charts/{chart_id}/current"
    table = table_fallback(pd.read_parquet(chart["snapshot"]["path"]))
    return f"""
<article class="chart-card" data-chart-id="{html.escape(chart_id)}" data-live-url="{html.escape(live_url)}">
  <header><div><h3>{html.escape(spec.get("title") or spec["kind"].replace("_", " ").title())}</h3>
  <p>Immutable snapshot captured {html.escape(captured)}</p></div>
  <div class="tabs"><button data-mode="snapshot" aria-pressed="true">Snapshot</button>
  <button data-mode="live" aria-pressed="false">Live</button></div></header>
  <div class="snapshot-chart chart" data-option="{html.escape(option_json(chart["option"]), quote=True)}"></div>
  {table}
  <div class="live-area" hidden><div class="live-chart chart"></div>
  <button data-refresh>Refresh current data</button><p class="status" aria-live="polite"></p>
  <div class="claims"></div></div>
</article>"""


def _research_notebook(
    service: KriskService,
    research: dict[str, Any],
    charts: list[dict[str, Any]],
    base_url: str,
) -> nbformat.NotebookNode:
    notebook = nbformat.v4.new_notebook()
    notebook.metadata["krisk"] = {
        "schema_version": 1,
        "research_id": research["id"],
        "created_at": research["created_at"],
        "live_base_url": base_url,
    }
    cells = [
        nbformat.v4.new_markdown_cell(f"# {research['question']}"),
        nbformat.v4.new_markdown_cell(
            "## Hypothesis\n\n" + (research.get("hypothesis") or "No hypothesis recorded.")
        ),
        nbformat.v4.new_markdown_cell(
            "## Methodology\n\n"
            + "\n".join(f"{index}. {item}" for index, item in enumerate(research["methodology"], 1))
        ),
    ]
    for query_id in research["query_ids"]:
        query = service.repository.get("query", query_id)
        if query:
            cells.append(
                nbformat.v4.new_markdown_cell(
                    f"### Query `{query_id}`\n\nSource: `{query['source']}`\n\n```sql\n{query['sql']}\n```"
                    f"\n\nSource fingerprint: `{query.get('source_fingerprint') or 'unavailable'}`"
                )
            )
    echarts = (
        Path(join_current_dir("static/echarts.min.js"))
        .read_text(encoding="utf-8")
        .replace("</script>", "<\\/script>")
    )
    for chart in charts:
        snapshot_path = chart["snapshot"]["path"]
        encoded = base64.b64encode(Path(snapshot_path).read_bytes()).decode("ascii")
        card = _living_card(chart, base_url)
        output_html = f"<script>{echarts}</script><style>{_research_css()}</style>{card}<script>{_research_js()}</script>"
        output = nbformat.v4.new_output(
            output_type="display_data",
            data={
                "text/html": output_html,
                "application/vnd.krisk.chart+json": chart["option"],
                "application/vnd.krisk.snapshot+parquet": encoded,
            },
            metadata={
                "krisk": {
                    "chart_id": chart["id"],
                    "snapshot_hash": chart["snapshot"]["hash"],
                    "captured_at": chart["snapshot"]["captured_at"],
                }
            },
        )
        cell = nbformat.v4.new_code_cell(
            source=(
                "# The saved output below is self-contained. Re-run this cell to fetch the current chart.\n"
                "from IPython.display import IFrame\n"
                f"IFrame('{base_url.rstrip('/')}/charts/{chart['id']}', width='100%', height=560)"
            ),
            outputs=[output],
            execution_count=None,
        )
        cells.append(cell)
    cells.extend(
        [
            nbformat.v4.new_markdown_cell(
                "## Findings\n\n" + "\n".join(f"- {item}" for item in research["findings"])
            ),
            nbformat.v4.new_markdown_cell(f"## Conclusion\n\n{research['conclusion']}"),
            nbformat.v4.new_markdown_cell(
                "## Limitations\n\n"
                + ("\n".join(f"- {item}" for item in research["limitations"]) or "None recorded.")
            ),
        ]
    )
    notebook.cells = cells
    return notebook


def _research_css() -> str:
    return """
:root{font-family:Inter,ui-sans-serif,system-ui,sans-serif;color:#172033;background:#f8fafc}
body{margin:0}main{max-width:980px;margin:auto;padding:48px 24px 80px}h1{font-size:clamp(2rem,5vw,4rem);line-height:1.04}
h2{margin-top:2.5rem}.eyebrow{text-transform:uppercase;letter-spacing:.14em;color:#4f46e5;font-weight:700}.meta,.chart-card header p,.status{color:#64748b}
.conclusion{font-size:1.25rem;border-left:4px solid #4f46e5;padding-left:1rem}.chart-card{background:white;border:1px solid #e2e8f0;border-radius:18px;padding:20px;margin:24px 0;box-shadow:0 12px 35px #0f172a12}
.chart-card header{display:flex;justify-content:space-between;align-items:start;gap:16px}.chart-card h3{margin:.2rem 0}.tabs{display:flex;gap:8px}.tabs button,button[data-refresh]{border:1px solid #cbd5e1;background:#f8fafc;border-radius:9px;padding:8px 12px;cursor:pointer}.tabs button[aria-pressed=true]{background:#312e81;color:white}.chart{height:420px;width:100%}.claims p{padding:8px 12px;background:#f1f5f9;border-radius:8px}
details{margin:1rem 0}table{border-collapse:collapse;width:100%;font-size:.9rem}th,td{border-bottom:1px solid #e2e8f0;padding:.5rem;text-align:left}
"""


def _research_js() -> str:
    return """
(() => { document.querySelectorAll('.chart-card').forEach((card) => {
  const escapeHtml=(value)=>String(value??'').replace(/[&<>\"']/g,(character)=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[character]));
  const snapshot = card.querySelector('.snapshot-chart');
  if (!snapshot.dataset.ready) { const chart = echarts.init(snapshot); chart.setOption(JSON.parse(snapshot.dataset.option)); snapshot.dataset.ready='1'; }
  const liveArea=card.querySelector('.live-area'); const buttons=card.querySelectorAll('[data-mode]'); let liveChart;
  async function refresh(){ const status=card.querySelector('.status'); status.textContent='Loading current data…';
    try { const response=await fetch(card.dataset.liveUrl); if(!response.ok) throw new Error(`server returned ${response.status}`); const data=await response.json();
      const element=card.querySelector('.live-chart'); liveChart ||= echarts.init(element); liveChart.setOption(data.option,true); liveChart.resize(); status.textContent=`Current as of ${data.refreshed_at}`;
      card.querySelector('.claims').innerHTML=(data.claims||[]).map(c=>`<p><strong>${escapeHtml(String(c.status).toUpperCase())}</strong> — ${escapeHtml(c.label)}: ${escapeHtml(c.message)}</p>`).join('');
    } catch(error){status.textContent=`Live data unavailable; saved evidence is unchanged. ${error.message}`;}}
  buttons.forEach(button=>button.addEventListener('click',()=>{const live=button.dataset.mode==='live'; snapshot.hidden=live; liveArea.hidden=!live; buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button))); if(live)refresh();}));
  card.querySelector('[data-refresh]').addEventListener('click',refresh);
});})();
"""
