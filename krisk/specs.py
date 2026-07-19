"""Typed, safe chart and research specifications."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Literal

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, model_validator

ChartKind = Literal[
    "bar",
    "line",
    "area",
    "histogram",
    "scatter",
    "waterfall",
    "combo",
    "pie",
    "doughnut",
    "sunburst",
    "kpi",
    "kpi_trend",
]
Aggregate = Literal["count", "sum", "mean", "median", "min", "max", "nunique"]


class ChartSpec(BaseModel):
    """A portable chart definition shared by notebooks, REST, and MCP."""

    model_config = ConfigDict(extra="forbid")

    version: Literal[1] = 1
    kind: ChartKind
    title: str = ""
    x: str | None = None
    y: str | None = None
    y2: str | None = None
    color: str | None = None
    size: str | None = None
    aggregate: Aggregate = "count"
    aggregate_y2: Aggregate = "mean"
    bins: int = Field(default=10, ge=1, le=200)
    density: bool = False
    stacked: bool = False
    smooth: bool = False
    annotate: bool = False
    theme: Literal["light", "dark"] = "light"
    width: str = "100%"
    height: int = Field(default=420, ge=160, le=2400)
    description: str | None = None
    sampling: Literal["D", "W", "M", "Q", "Y"] | None = None
    date_format: str = "%Y-%m-%d"
    number_font_size: int = Field(default=48, ge=12, le=160)
    comparison_font_size: int = Field(default=18, ge=10, le=80)
    safe_overrides: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_encoding(self) -> ChartSpec:
        required: dict[str, tuple[str, ...]] = {
            "bar": ("x",),
            "line": ("x",),
            "area": ("x",),
            "histogram": ("x",),
            "scatter": ("x", "y"),
            "waterfall": ("x", "y"),
            "combo": ("x", "y", "y2"),
            "pie": ("x",),
            "doughnut": ("x",),
            "sunburst": ("x", "color"),
            "kpi": ("y",),
            "kpi_trend": ("x", "y"),
        }
        missing = [name for name in required[self.kind] if not getattr(self, name)]
        if missing:
            raise ValueError(f"{self.kind} requires: {', '.join(missing)}")
        _reject_executable_values(self.safe_overrides)
        return self


class QueryRecord(BaseModel):
    id: str
    source: str
    sql: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    columns: list[str] = Field(default_factory=list)
    source_fingerprint: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ClaimKind(StrEnum):
    THRESHOLD = "threshold"
    RANGE = "range"
    COMPARISON = "comparison"
    CHANGE = "change"


class ClaimSpec(BaseModel):
    """A machine-checkable statement backed by a one-row query result."""

    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    label: str
    kind: ClaimKind
    query_id: str
    value_column: str = "value"
    operator: Literal["gt", "gte", "lt", "lte", "eq", "neq", "between"] = "gte"
    expected: float | str | bool | None = None
    maximum: float | None = None
    compare_column: str | None = None
    warning_tolerance: float | None = Field(default=None, ge=0)
    narrative: str | None = None

    @model_validator(mode="after")
    def validate_semantics(self) -> ClaimSpec:
        threshold_operators = {"gt", "gte", "lt", "lte", "eq", "neq"}
        if self.kind is ClaimKind.THRESHOLD:
            if self.operator not in threshold_operators or self.expected is None:
                raise ValueError("Threshold claims require an expected value and scalar operator")
            if self.compare_column:
                raise ValueError("Threshold claims cannot use compare_column")
        elif self.kind is ClaimKind.RANGE:
            if self.operator != "between" or not isinstance(self.expected, (int, float)):
                raise ValueError("Range claims require between and a numeric minimum")
            if self.maximum is None or self.expected > self.maximum:
                raise ValueError("Range claims require a maximum at or above the minimum")
        elif self.kind in {ClaimKind.COMPARISON, ClaimKind.CHANGE}:
            if self.operator not in threshold_operators or not self.compare_column:
                raise ValueError(
                    "Comparison and change claims require compare_column and scalar operator"
                )
        if self.warning_tolerance is not None and self.operator == "eq":
            raise ValueError("Equality claims do not support warning_tolerance")
        return self


class ClaimResult(BaseModel):
    claim_id: str
    label: str
    status: Literal["pass", "warn", "fail", "unknown"]
    observed: Any = None
    expected: Any = None
    message: str


class ResearchDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    question: str
    hypothesis: str | None = None
    methodology: list[str]
    query_ids: list[str] = Field(default_factory=list)
    chart_ids: list[str] = Field(default_factory=list)
    findings: list[str]
    conclusion: str
    limitations: list[str] = Field(default_factory=list)
    claims: list[ClaimSpec] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


def as_dataframe(data: Any) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data.copy()
    if isinstance(data, pd.Series):
        return data.to_frame()
    if hasattr(data, "to_pandas"):
        result = data.to_pandas()
        return result if isinstance(result, pd.DataFrame) else pd.DataFrame(result)
    if hasattr(data, "execute"):
        result = data.execute()
        return result if isinstance(result, pd.DataFrame) else pd.DataFrame(result)
    return pd.DataFrame(data)


def jsonable(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.isoformat()
    if isinstance(value, np.ndarray):
        return [jsonable(item) for item in value.tolist()]
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if pd.isna(value):
        return None
    return str(value)


def _reject_executable_values(value: Any, path: str = "safe_overrides") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).lower()
            executable_key = lowered.startswith("on") or lowered in {"formatter", "renderitem"}
            executable_value = callable(item) or isinstance(item, str)
            if executable_key and executable_value:
                raise ValueError(f"Executable JavaScript is not allowed at {path}.{key}")
            _reject_executable_values(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_executable_values(item, f"{path}[{index}]")
    elif callable(value):
        raise ValueError(f"Callables are not allowed at {path}")
    elif isinstance(value, str):
        lowered = value.casefold()
        if "=>" in value or "function" in lowered or "javascript:" in lowered:
            raise ValueError(f"Executable JavaScript is not allowed at {path}")
