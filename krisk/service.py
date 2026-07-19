"""Application service shared by Python, REST, and MCP."""

from __future__ import annotations

import operator
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from krisk.chart.api import Chart
from krisk.sources import SourceRegistry
from krisk.specs import (
    ChartSpec,
    ClaimResult,
    ClaimSpec,
    QueryRecord,
    ResearchDraft,
    jsonable,
)
from krisk.storage import ArtifactStore, Repository, default_repository


class NotFoundError(KeyError):
    pass


MAX_QUERY_ROWS = 10_000
MAX_SNAPSHOT_ROWS = 10_000
MAX_SNAPSHOT_BYTES = 5 * 1024 * 1024


class KriskService:
    def __init__(
        self,
        sources: SourceRegistry,
        repository: Repository | None = None,
        artifacts: ArtifactStore | None = None,
    ) -> None:
        self.sources = sources
        self.repository = repository or default_repository()
        self.artifacts = artifacts or ArtifactStore(Path("var/krisk/artifacts"))

    def list_sources(self) -> list[dict[str, str]]:
        return self.sources.list_sources()

    def inspect_source(self, source: str, relation: str | None = None) -> dict[str, Any]:
        adapter = self.sources.get(source)
        if relation:
            return {"source": source, "relation": relation, "columns": adapter.describe(relation)}
        return {"source": source, "relations": adapter.list_relations()}

    def run_query(
        self,
        source: str,
        sql: str,
        parameters: dict[str, Any] | None = None,
        preview_rows: int = 200,
    ) -> dict[str, Any]:
        adapter = self.sources.get(source)
        frame = adapter.execute(sql, parameters, limit=MAX_QUERY_ROWS)
        query_id = str(uuid.uuid4())
        record = QueryRecord(
            id=query_id,
            source=source,
            sql=sql,
            parameters=parameters or {},
            columns=[str(column) for column in frame.columns],
            source_fingerprint=adapter.fingerprint(),
        )
        self.repository.save("query", query_id, record.model_dump(mode="json"))
        return {
            "query": record.model_dump(mode="json"),
            "row_count": len(frame),
            "preview": jsonable(frame.head(preview_rows).to_dict(orient="records")),
        }

    def execute_saved_query(self, query_id: str) -> pd.DataFrame:
        payload = self.repository.get("query", query_id)
        if not payload:
            raise NotFoundError(f"Unknown query: {query_id}")
        record = QueryRecord.model_validate(payload)
        return self.sources.get(record.source).execute(
            record.sql,
            record.parameters,
            limit=MAX_QUERY_ROWS,
        )

    def create_chart(self, query_id: str, spec: ChartSpec | dict[str, Any]) -> dict[str, Any]:
        parsed = spec if isinstance(spec, ChartSpec) else ChartSpec.model_validate(spec)
        frame = self.execute_saved_query(query_id)
        chart = Chart.from_dataframe(frame, parsed)
        snapshot = chart.snapshot_data if chart.snapshot_data is not None else frame
        if len(snapshot) > MAX_SNAPSHOT_ROWS:
            raise ValueError(
                f"Chart snapshot exceeds {MAX_SNAPSHOT_ROWS:,} rows; aggregate or downsample the query"
            )
        digest, path, _ = self.artifacts.save_frame(snapshot, max_bytes=MAX_SNAPSHOT_BYTES)
        chart_id = str(uuid.uuid4())
        payload = {
            "id": chart_id,
            "query_id": query_id,
            "spec": parsed.model_dump(mode="json"),
            "option": chart.option,
            "snapshot": {
                "hash": digest,
                "path": str(path),
                "row_count": len(snapshot),
                "captured_at": datetime.now(UTC).isoformat(),
            },
        }
        self.repository.save("chart", chart_id, payload)
        return payload

    def get_chart(self, chart_id: str) -> dict[str, Any]:
        payload = self.repository.get("chart", chart_id)
        if not payload:
            raise NotFoundError(f"Unknown chart: {chart_id}")
        return payload

    def list_charts(self) -> list[dict[str, Any]]:
        return self.repository.list("chart")

    def refresh_chart(self, chart_id: str) -> dict[str, Any]:
        payload = self.get_chart(chart_id)
        frame = self.execute_saved_query(payload["query_id"])
        chart = Chart.from_dataframe(frame, ChartSpec.model_validate(payload["spec"]))
        return {
            "chart_id": chart_id,
            "option": chart.option,
            "refreshed_at": datetime.now(UTC).isoformat(),
            "snapshot_hash": payload["snapshot"]["hash"],
            "claims": self.claims_for_chart(chart_id),
        }

    def claims_for_chart(self, chart_id: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for payload in self.repository.list("research"):
            if chart_id not in payload.get("chart_ids", []):
                continue
            research = ResearchDraft.model_validate(payload)
            results.extend(
                self.evaluate_claim(claim).model_dump(mode="json") for claim in research.claims
            )
        return results

    def save_research(self, draft: ResearchDraft | dict[str, Any]) -> dict[str, Any]:
        parsed = draft if isinstance(draft, ResearchDraft) else ResearchDraft.model_validate(draft)
        for query_id in set(parsed.query_ids + [claim.query_id for claim in parsed.claims]):
            if not self.repository.get("query", query_id):
                raise NotFoundError(f"Research references unknown query: {query_id}")
        for chart_id in parsed.chart_ids:
            if not self.repository.get("chart", chart_id):
                raise NotFoundError(f"Research references unknown chart: {chart_id}")
        research_id = parsed.id or str(uuid.uuid4())
        values = parsed.model_copy(update={"id": research_id}).model_dump(mode="json")
        for claim in values["claims"]:
            claim["id"] = claim.get("id") or str(uuid.uuid4())
        self.repository.save("research", research_id, values)
        return values

    def get_research(self, research_id: str) -> dict[str, Any]:
        payload = self.repository.get("research", research_id)
        if not payload:
            raise NotFoundError(f"Unknown research: {research_id}")
        return payload

    def list_research(self) -> list[dict[str, Any]]:
        return self.repository.list("research")

    def evaluate_research(self, research_id: str) -> list[dict[str, Any]]:
        research = ResearchDraft.model_validate(self.get_research(research_id))
        return [self.evaluate_claim(claim).model_dump(mode="json") for claim in research.claims]

    def evaluate_claim(self, claim: ClaimSpec) -> ClaimResult:
        claim_id = claim.id or "unsaved"
        try:
            frame = self.execute_saved_query(claim.query_id)
            if len(frame) != 1 or claim.value_column not in frame:
                raise ValueError("Claim query must return one row containing the value column")
            observed = jsonable(frame.iloc[0][claim.value_column])
            expected: Any = claim.expected
            if claim.compare_column:
                if claim.compare_column not in frame:
                    raise ValueError(f"Missing comparison column: {claim.compare_column}")
                expected = jsonable(frame.iloc[0][claim.compare_column])
            passed = _compare(observed, claim.operator, expected, claim.maximum)
            status: Literal["pass", "warn", "fail"] = "pass" if passed else "fail"
            if passed and _near_claim_boundary(observed, expected, claim):
                status = "warn"
            return ClaimResult(
                claim_id=claim_id,
                label=claim.label,
                status=status,
                observed=observed,
                expected=expected,
                message=f"Observed {observed!r}; expected {claim.operator} {expected!r}",
            )
        except Exception as error:
            return ClaimResult(
                claim_id=claim_id,
                label=claim.label,
                status="unknown",
                message=str(error),
            )


def _compare(observed: Any, name: str, expected: Any, maximum: float | None) -> bool:
    functions = {
        "gt": operator.gt,
        "gte": operator.ge,
        "lt": operator.lt,
        "lte": operator.le,
        "eq": operator.eq,
        "neq": operator.ne,
    }
    if name == "between":
        if maximum is None:
            raise ValueError("Between claims require maximum")
        return bool(expected <= observed <= maximum)
    if name not in functions:
        raise ValueError(f"Unsupported claim operator: {name}")
    return bool(functions[name](observed, expected))


def _near_claim_boundary(observed: Any, expected: Any, claim: ClaimSpec) -> bool:
    tolerance = claim.warning_tolerance
    if tolerance is None or not isinstance(observed, (int, float)):
        return False
    if claim.operator == "between":
        return bool(
            isinstance(expected, (int, float))
            and claim.maximum is not None
            and min(abs(observed - expected), abs(claim.maximum - observed)) <= tolerance
        )
    return bool(
        claim.operator != "eq"
        and isinstance(expected, (int, float))
        and abs(observed - expected) <= tolerance
    )
