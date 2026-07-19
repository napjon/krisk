import base64
from pathlib import Path

import nbformat
import pandas as pd
from fastapi.testclient import TestClient

from krisk.export import export_research
from krisk.server import create_app
from krisk.service import KriskService
from krisk.sources import FrameSource, SourceRegistry
from krisk.storage import ArtifactStore, MemoryRepository


def make_service(tmp_path):
    frame = pd.DataFrame({"day": ["Mon", "Tue"], "orders": [12, 18]})
    return KriskService(
        SourceRegistry({"demo": FrameSource({"orders": frame})}),
        MemoryRepository(),
        ArtifactStore(tmp_path / "artifacts"),
    )


def save_fixture(service):
    query = service.run_query("demo", "SELECT day, orders FROM orders")
    metric = service.run_query("demo", "SELECT sum(orders) AS value FROM orders")
    chart = service.create_chart(
        query["query"]["id"],
        {"kind": "bar", "x": "day", "y": "orders", "aggregate": "sum", "title": "Orders"},
    )
    research = service.save_research(
        {
            "question": "How many orders were recorded?",
            "methodology": ["Summed orders by day."],
            "query_ids": [query["query"]["id"], metric["query"]["id"]],
            "chart_ids": [chart["id"]],
            "findings": ["Thirty orders were recorded."],
            "conclusion": "Recorded orders total 30 at capture time.",
            "limitations": ["Demo data only."],
            "claims": [
                {
                    "label": "Orders remain at least 30",
                    "kind": "threshold",
                    "query_id": metric["query"]["id"],
                    "operator": "gte",
                    "expected": 30,
                }
            ],
        }
    )
    return chart, research


def test_rest_vertical_slice(tmp_path):
    service = make_service(tmp_path)
    with TestClient(create_app(service)) as client:
        assert client.get("/health").json() == {"status": "ok", "sources": 1}
        query = client.post(
            "/api/v1/queries",
            json={"source": "demo", "sql": "SELECT day, orders FROM orders"},
        )
        assert query.status_code == 200
        chart = client.post(
            "/api/v1/charts",
            json={
                "query_id": query.json()["query"]["id"],
                "spec": {"kind": "bar", "x": "day", "y": "orders", "aggregate": "sum"},
            },
        )
        assert chart.status_code == 200
        chart_id = chart.json()["id"]
        assert client.get(f"/api/v1/charts/{chart_id}/current").status_code == 200
        assert "Snapshot" in client.get(f"/charts/{chart_id}").text
        assert client.get("/api/v1/charts").json()[0]["id"] == chart_id
        assert "Research the present" in client.get("/").text
        assert client.get("/simpleRequestServer").json()["series"][0]["type"] == "line"


def test_research_exports_embed_snapshot_not_live_data(tmp_path):
    service = make_service(tmp_path)
    chart, research = save_fixture(service)
    paths = export_research(service, research["id"], tmp_path / "exports")
    html = Path(paths["html"]).read_text()
    assert "Snapshot" in html and "Live" in html
    assert "Sources and provenance" in html
    assert "Claim status at export" in html
    assert "View chart data as a table" in html
    assert f"/api/v1/charts/{chart['id']}/current" in html
    notebook = nbformat.read(paths["ipynb"], as_version=4)
    snapshot_output = next(cell.outputs[0] for cell in notebook.cells if cell.cell_type == "code")
    encoded = snapshot_output.data["application/vnd.krisk.snapshot+parquet"]
    assert base64.b64decode(encoded).startswith(b"PAR1")
    assert notebook.metadata["krisk"]["research_id"] == research["id"]

    with TestClient(create_app(service)) as client:
        report = client.get(f"/research/{research['id']}")
        assert report.status_code == 200
        assert research["question"] in report.text


def test_research_export_can_select_one_format(tmp_path):
    service = make_service(tmp_path)
    _, research = save_fixture(service)

    paths = export_research(
        service,
        research["id"],
        tmp_path / "html-only",
        output_format="html",
    )

    assert set(paths) == {"html"}
    assert Path(paths["html"]).exists()
    assert not list((tmp_path / "html-only").glob("*.ipynb"))
