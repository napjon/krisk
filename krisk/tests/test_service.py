from pathlib import Path

import pandas as pd
import pytest

from krisk.service import KriskService
from krisk.sources import FrameSource, SourceError, SourceRegistry, validate_readonly_sql
from krisk.specs import ChartSpec, ResearchDraft
from krisk.storage import ArtifactStore, MemoryRepository, SQLiteRepository


@pytest.fixture
def service(tmp_path):
    frame = pd.DataFrame(
        {
            "month": ["Jan", "Feb", "Mar"],
            "revenue": [100.0, 120.0, 140.0],
        }
    )
    return KriskService(
        SourceRegistry({"demo": FrameSource({"sales": frame})}),
        MemoryRepository(),
        ArtifactStore(tmp_path / "artifacts"),
    )


def test_query_chart_research_and_claim_round_trip(service, tmp_path):
    query = service.run_query("demo", "SELECT month, revenue FROM sales")
    metric = service.run_query("demo", "SELECT sum(revenue) AS value FROM sales")
    chart = service.create_chart(
        query["query"]["id"],
        ChartSpec(kind="line", x="month", y="revenue", aggregate="sum"),
    )
    research = service.save_research(
        ResearchDraft(
            question="Is revenue above the target?",
            methodology=["Summed recorded revenue and compared it with 300."],
            query_ids=[query["query"]["id"], metric["query"]["id"]],
            chart_ids=[chart["id"]],
            findings=["Recorded total revenue is 360."],
            conclusion="Revenue is above the target at capture time.",
            claims=[
                {
                    "label": "Revenue remains above target",
                    "kind": "threshold",
                    "query_id": metric["query"]["id"],
                    "operator": "gte",
                    "expected": 300,
                }
            ],
        )
    )
    assert Path(chart["snapshot"]["path"]).exists()
    assert len(query["query"]["source_fingerprint"]) == 64
    assert chart["snapshot"]["hash"] == service.refresh_chart(chart["id"])["snapshot_hash"]
    assert service.evaluate_research(research["id"])[0]["status"] == "pass"


@pytest.mark.parametrize(
    "sql",
    ["DELETE FROM sales", "DROP TABLE sales", "SELECT 1; SELECT 2", "PRAGMA version"],
)
def test_sql_guard_rejects_mutation(sql):
    with pytest.raises(SourceError):
        validate_readonly_sql(sql)


def test_query_limit_is_enforced():
    source = FrameSource({"rows": pd.DataFrame({"value": range(4)})})
    with pytest.raises(SourceError, match="row result limit"):
        source.execute("SELECT * FROM rows", limit=2)


def test_sqlite_repository_survives_restart(tmp_path):
    repository = SQLiteRepository(tmp_path / "krisk.db")
    record_id = "9bc4d2c0-61d5-4856-a0d4-2aeaf008b24e"
    repository.save("chart", record_id, {"id": record_id, "title": "Durable"})

    restarted = SQLiteRepository(tmp_path / "krisk.db")
    assert restarted.get("chart", record_id)["title"] == "Durable"
    assert restarted.list("chart")[0]["id"] == record_id
