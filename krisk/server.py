"""Local REST and MCP server."""

from __future__ import annotations

import contextlib
import html
import os
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from krisk.export import export_research as write_research_export
from krisk.export import render_research_html
from krisk.rendering import standalone_html
from krisk.service import KriskService, NotFoundError
from krisk.sources import SourceError, SourceRegistry
from krisk.specs import ChartSpec, ResearchDraft


class QueryRequest(BaseModel):
    source: str
    sql: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class ChartRequest(BaseModel):
    query_id: str
    spec: ChartSpec


class ExportRequest(BaseModel):
    output_dir: str = "var/krisk/exports"
    base_url: str = "http://127.0.0.1:8060"
    format: Literal["html", "ipynb", "both"] = "both"


def default_service() -> KriskService:
    config = Path(os.environ.get("KRISK_CONFIG", "krisk.toml"))
    return KriskService(SourceRegistry.from_toml(config))


def create_mcp(service: KriskService) -> FastMCP:
    mcp = FastMCP(
        "Krisk Living Research",
        instructions=(
            "Inspect named read-only sources, save evidence-backed charts, and convert concluded "
            "analyses into reproducible living research. Never invent query results."
        ),
        stateless_http=True,
        json_response=True,
    )
    mcp.settings.streamable_http_path = "/"

    @mcp.tool()
    def list_sources() -> list[dict[str, str]]:
        """List named data sources available to this Krisk server."""
        return service.list_sources()

    @mcp.tool()
    def inspect_source(source: str, relation: str | None = None) -> dict[str, Any]:
        """List relations or describe one relation before writing a query."""
        return service.inspect_source(source, relation)

    @mcp.tool()
    def run_query(
        source: str, sql: str, parameters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Run one bounded, read-only SELECT query and return a preview plus stable query ID."""
        return service.run_query(source, sql, parameters)

    @mcp.tool()
    def create_chart(query_id: str, spec: dict[str, Any]) -> dict[str, Any]:
        """Create and snapshot a typed chart from a saved query."""
        return service.create_chart(query_id, spec)

    @mcp.tool()
    def refresh_chart(chart_id: str) -> dict[str, Any]:
        """Re-run a chart query without changing its immutable saved snapshot."""
        return service.refresh_chart(chart_id)

    @mcp.tool()
    def save_research(research: dict[str, Any]) -> dict[str, Any]:
        """Save an explicitly requested, evidence-backed structured research record."""
        return service.save_research(research)

    @mcp.tool()
    def evaluate_research(research_id: str) -> list[dict[str, Any]]:
        """Re-run typed claims and report pass, warn, fail, or unknown."""
        return service.evaluate_research(research_id)

    @mcp.tool()
    def export_research(
        research_id: str,
        output_dir: str = "var/krisk/exports",
        base_url: str = "http://127.0.0.1:8060",
        format: Literal["html", "ipynb", "both"] = "both",
    ) -> dict[str, str]:
        """Export saved research to a static/live HTML page and Jupyter notebook."""
        return write_research_export(service, research_id, Path(output_dir), base_url, format)

    @mcp.tool()
    def export_saved_research(
        research_id: str,
        output_dir: str = "var/krisk/exports",
        base_url: str = "http://127.0.0.1:8060",
        format: Literal["html", "ipynb", "both"] = "both",
    ) -> dict[str, str]:
        """Compatibility alias for export_research."""
        return write_research_export(service, research_id, Path(output_dir), base_url, format)

    @mcp.resource("krisk://research/{research_id}")
    def research_resource(research_id: str) -> dict[str, Any]:
        return service.get_research(research_id)

    @mcp.resource("krisk://chart/{chart_id}/snapshot")
    def chart_resource(chart_id: str) -> dict[str, Any]:
        return service.get_chart(chart_id)

    @mcp.resource("krisk://chart/{chart_id}/current")
    def current_chart_resource(chart_id: str) -> dict[str, Any]:
        return service.refresh_chart(chart_id)

    @mcp.resource("krisk://research/{research_id}/export-manifest")
    def export_manifest_resource(research_id: str) -> dict[str, Any]:
        research = service.get_research(research_id)
        return {
            "research_id": research_id,
            "formats": ["html", "ipynb"],
            "tool": "export_research",
            "default_output_dir": "var/krisk/exports",
            "chart_ids": research["chart_ids"],
        }

    @mcp.prompt()
    def research_methodology(question: str) -> str:
        return (
            f"Investigate {question!r}. Inspect the source before querying; retain query and chart IDs; "
            "separate observations from inferences; record limitations; and only save research after "
            "the user confirms the conclusion."
        )

    return mcp


def create_app(service: KriskService | None = None) -> FastAPI:
    service = service or default_service()
    mcp = create_mcp(service)

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        async with mcp.session_manager.run():
            yield

    app = FastAPI(title="Krisk", version="0.9.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "null",
            "http://127.0.0.1:8060",
            "http://localhost:8060",
            "http://127.0.0.1:8888",
            "http://localhost:8888",
        ],
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type", "Accept", "Mcp-Session-Id"],
        expose_headers=["Mcp-Session-Id"],
    )

    @app.exception_handler(NotFoundError)
    async def missing_handler(request, error):
        return _json_error(404, str(error))

    @app.exception_handler(SourceError)
    async def source_handler(request, error):
        return _json_error(400, str(error))

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "sources": len(service.list_sources())}

    @app.api_route("/simpleRequestServer", methods=["GET", "POST"], deprecated=True)
    def flarisk_compatibility() -> dict[str, Any]:
        """Retain Flarisk's original demonstration endpoint for existing clients."""
        return {
            "title": {"text": "ECharts in Material-UI Card"},
            "xAxis": {
                "type": "category",
                "data": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            },
            "yAxis": {"type": "value"},
            "series": [{"data": [820, 932, 901, 934, 1290, 1330], "type": "line"}],
        }

    @app.get("/", response_class=HTMLResponse)
    def home() -> str:
        return _dashboard_html(service)

    @app.get("/api/v1/sources")
    def sources() -> list[dict[str, str]]:
        return service.list_sources()

    @app.get("/api/v1/sources/{source}")
    def inspect(source: str, relation: str | None = None) -> dict[str, Any]:
        return service.inspect_source(source, relation)

    @app.post("/api/v1/queries")
    def query(request: QueryRequest) -> dict[str, Any]:
        return service.run_query(request.source, request.sql, request.parameters)

    @app.post("/api/v1/charts")
    def chart(request: ChartRequest) -> dict[str, Any]:
        return service.create_chart(request.query_id, request.spec)

    @app.get("/api/v1/charts/{chart_id}")
    def get_chart(chart_id: str) -> dict[str, Any]:
        return service.get_chart(chart_id)

    @app.get("/api/v1/charts")
    def list_charts() -> list[dict[str, Any]]:
        return service.list_charts()

    @app.get("/api/v1/charts/{chart_id}/current")
    def current_chart(chart_id: str) -> dict[str, Any]:
        return service.refresh_chart(chart_id)

    @app.get("/charts/{chart_id}", response_class=HTMLResponse)
    def view_chart(chart_id: str) -> str:
        payload = service.get_chart(chart_id)
        return standalone_html(
            payload["option"],
            payload["id"],
            payload["spec"].get("title", "Krisk chart"),
            payload["spec"].get("height", 420),
            payload["spec"].get("description"),
            f"/api/v1/charts/{chart_id}/current",
            service.artifacts.load_frame(payload["snapshot"]["path"]),
        )

    @app.get("/research/{research_id}", response_class=HTMLResponse)
    def view_research(research_id: str) -> str:
        return render_research_html(service, research_id)

    @app.post("/api/v1/research")
    def research(request: ResearchDraft) -> dict[str, Any]:
        return service.save_research(request)

    @app.get("/api/v1/research/{research_id}")
    def get_research(research_id: str) -> dict[str, Any]:
        return service.get_research(research_id)

    @app.get("/api/v1/research")
    def list_research() -> list[dict[str, Any]]:
        return service.list_research()

    @app.get("/api/v1/research/{research_id}/evaluate")
    def evaluate(research_id: str) -> list[dict[str, Any]]:
        return service.evaluate_research(research_id)

    @app.post("/api/v1/research/{research_id}/export")
    def export(research_id: str, request: ExportRequest) -> dict[str, str]:
        return write_research_export(
            service,
            research_id,
            Path(request.output_dir),
            request.base_url,
            request.format,
        )

    app.mount("/mcp", mcp.streamable_http_app())
    app.state.krisk_service = service
    app.state.krisk_mcp = mcp
    return app


def _json_error(status: int, message: str):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=status, content={"detail": message.strip("'")})


def _dashboard_html(service: KriskService) -> str:
    charts = service.list_charts()[:12]
    research = service.list_research()[:12]
    chart_cards = (
        "".join(
            f'<a class="card" href="/charts/{html.escape(chart["id"], quote=True)}">'
            f'<span class="tag">{html.escape(chart["spec"]["kind"])}</span>'
            f"<h3>{html.escape(chart['spec'].get('title') or 'Untitled chart')}</h3>"
            f"<p>Snapshot · {html.escape(chart['snapshot']['captured_at'])}</p></a>"
            for chart in charts
        )
        or '<div class="empty">No saved charts yet. Create one through a notebook, REST, or MCP.</div>'
    )
    research_cards = (
        "".join(
            f'<a class="card" href="/research/{html.escape(item["id"], quote=True)}"><span class="tag">living research</span>'
            f"<h3>{html.escape(item['question'])}</h3>"
            f"<p>{len(item.get('chart_ids', []))} charts · {len(item.get('claims', []))} live claims</p>"
            f"<code>{html.escape(item['id'])}</code></a>"
            for item in research
        )
        or '<div class="empty">Concluded investigations will appear here with durable evidence.</div>'
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Krisk · Living research</title>
<style>
:root{{font-family:Inter,ui-sans-serif,system-ui,sans-serif;color:#172033;background:#f7f8fc}}*{{box-sizing:border-box}}
body{{margin:0}}main{{max-width:1180px;margin:auto;padding:56px 24px 90px}}header{{display:grid;grid-template-columns:1.7fr 1fr;gap:32px;align-items:end;margin-bottom:55px}}
.eyebrow,.tag{{text-transform:uppercase;letter-spacing:.13em;font-weight:750;color:#635bff;font-size:.76rem}}h1{{font-size:clamp(3rem,8vw,6.2rem);line-height:.9;letter-spacing:-.06em;margin:.4rem 0 1.2rem;max-width:850px}}.lead{{font-size:1.2rem;color:#596579;line-height:1.65}}
.status{{background:#111827;color:white;padding:22px;border-radius:20px}}.status strong{{font-size:2rem;display:block}}section{{margin-top:48px}}.section-head{{display:flex;align-items:baseline;justify-content:space-between}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}
.card,.empty{{display:block;background:white;border:1px solid #e5e7eb;border-radius:18px;padding:22px;text-decoration:none;color:inherit;min-height:150px;box-shadow:0 14px 38px #1118270a}}a.card:hover{{transform:translateY(-2px);border-color:#a5b4fc}}.card h3{{font-size:1.25rem;margin:.7rem 0}}.card p,.empty{{color:#64748b}}code{{font-size:.7rem;color:#64748b}}@media(max-width:720px){{header{{grid-template-columns:1fr}}}}
</style></head><body><main><header><div><p class="eyebrow">Krisk · evidence that stays alive</p><h1>Research the present. Preserve the proof.</h1>
<p class="lead">Explore read-only data with your preferred LLM, capture the conclusion as reproducible research, and revisit live charts without changing the original snapshot.</p></div>
<div class="status"><span>Server ready</span><strong>{len(service.list_sources())}</strong><span>connected data sources</span><p>MCP <code>/mcp/</code> · REST <code>/api/v1</code></p></div></header>
<section><div class="section-head"><h2>Recent charts</h2><span>{len(charts)} saved</span></div><div class="grid">{chart_cards}</div></section>
<section><div class="section-head"><h2>Living research</h2><span>{len(research)} saved</span></div><div class="grid">{research_cards}</div></section>
</main></body></html>"""


app = create_app()
