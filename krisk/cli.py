"""Krisk command-line interface."""

from __future__ import annotations

import os
from importlib import resources
from pathlib import Path
from typing import Literal, cast

import pandas as pd
import typer

from krisk.chart.api import Chart
from krisk.export import export_research
from krisk.server import create_mcp, default_service
from krisk.specs import ChartSpec

app = typer.Typer(help="Krisk charts, MCP, and living research")
sources_app = typer.Typer(help="Validate and inspect named data sources")
research_app = typer.Typer(help="Export and evaluate saved research")
app.add_typer(sources_app, name="sources")
app.add_typer(research_app, name="research")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1"),
    port: int = typer.Option(8060),
) -> None:
    """Run the local REST and Streamable HTTP MCP server."""
    if host not in {"127.0.0.1", "localhost", "::1"} and not os.environ.get(
        "KRISK_ALLOW_INSECURE_REMOTE_BIND"
    ):
        raise typer.BadParameter(
            "Krisk 0.9 is unauthenticated; remote binding requires "
            "KRISK_ALLOW_INSECURE_REMOTE_BIND=1"
        )
    import uvicorn

    uvicorn.run("krisk.server:app", host=host, port=port, reload=False)


@app.command()
def mcp() -> None:
    """Run Krisk MCP over stdio for a local LLM host."""
    create_mcp(default_service()).run(transport="stdio")


@app.command()
def demo(output: Path = Path("var/krisk/demo.html")) -> None:
    """Create a self-contained chart without a database or server."""
    data = pd.DataFrame(
        {
            "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "revenue": [82, 93, 90, 112, 129, 141],
        }
    )
    chart = Chart.from_dataframe(
        data,
        ChartSpec(
            kind="area",
            x="month",
            y="revenue",
            aggregate="sum",
            title="Revenue trend",
            description="Monthly demo revenue",
            smooth=True,
        ),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    chart.to_html(output)
    typer.echo(str(output.resolve()))


@app.command("skill-path")
def skill_path() -> None:
    """Print the bundled portable research skill directory."""
    package_skill = resources.files("krisk").joinpath("skills/save-research-notebook")
    if package_skill.is_dir():
        typer.echo(str(package_skill))
        return
    repository_skill = Path(__file__).resolve().parent.parent / "skills/save-research-notebook"
    typer.echo(str(repository_skill))


@sources_app.command("validate")
def validate_sources() -> None:
    service = default_service()
    for source in service.list_sources():
        name = source["name"]
        relations = service.inspect_source(name)["relations"]
        typer.echo(f"{name}: ok ({len(relations)} relations)")


@research_app.command("export")
def export_command(
    research_id: str,
    output_dir: Path = Path("var/krisk/exports"),
    base_url: str = "http://127.0.0.1:8060",
    format: str = typer.Option("both", "--format", help="html, ipynb, or both"),
) -> None:
    if format not in {"html", "ipynb", "both"}:
        raise typer.BadParameter("format must be html, ipynb, or both")
    output_format = cast(Literal["html", "ipynb", "both"], format)
    paths = export_research(default_service(), research_id, output_dir, base_url, output_format)
    for kind, path in paths.items():
        typer.echo(f"{kind}: {Path(path).resolve()}")


if __name__ == "__main__":
    app()
