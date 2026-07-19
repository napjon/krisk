"""Compile typed chart specifications into safe ECharts options."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import numpy as np
import pandas as pd

from krisk.specs import ChartSpec, as_dataframe, jsonable

PALETTE = ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de", "#3ba272"]


def compile_chart(data: Any, spec: ChartSpec) -> tuple[dict[str, Any], pd.DataFrame]:
    frame = as_dataframe(data)
    _validate_columns(frame, spec)
    option, materialized = _compile(frame, spec)
    option.setdefault("title", {"text": spec.title})
    option.setdefault("color", PALETTE)
    option.setdefault("aria", {"enabled": True, "decal": {"show": True}})
    option.setdefault("animation", False)
    _deep_merge(option, deepcopy(spec.safe_overrides))
    return jsonable(option), materialized


def _compile(frame: pd.DataFrame, spec: ChartSpec) -> tuple[dict[str, Any], pd.DataFrame]:
    if spec.kind in {"bar", "line", "area"}:
        return _axis_chart(frame, spec)
    if spec.kind == "histogram":
        return _histogram(frame, spec)
    if spec.kind == "scatter":
        return _scatter(frame, spec)
    if spec.kind == "waterfall":
        return _waterfall(frame, spec)
    if spec.kind == "combo":
        return _combo(frame, spec)
    if spec.kind in {"pie", "doughnut", "sunburst"}:
        return _pie(frame, spec)
    if spec.kind in {"kpi", "kpi_trend"}:
        return _kpi(frame, spec)
    raise ValueError(f"Unsupported chart kind: {spec.kind}")


def _aggregate(frame: pd.DataFrame, groups: list[str], value: str | None, how: str) -> pd.DataFrame:
    if not groups:
        if value is None or how == "count":
            result = len(frame)
        else:
            series = frame[value]
            method = "nunique" if how == "nunique" else how
            result = getattr(series, method)()
        return pd.DataFrame({"value": [result]})
    if value is None or how == "count":
        return frame.groupby(groups, dropna=False, sort=False).size().rename("value").reset_index()
    grouped = frame.groupby(groups, dropna=False, sort=False)[value]
    method = "nunique" if how == "nunique" else how
    return getattr(grouped, method)().rename("value").reset_index()


def _axis_chart(frame: pd.DataFrame, spec: ChartSpec) -> tuple[dict[str, Any], pd.DataFrame]:
    assert spec.x
    groups = [spec.x] + ([spec.color] if spec.color else [])
    materialized = _aggregate(frame, groups, spec.y, spec.aggregate)
    categories = list(dict.fromkeys(materialized[spec.x].map(jsonable)))
    series_type = "line" if spec.kind in {"line", "area"} else "bar"
    series: list[dict[str, Any]] = []
    if spec.color:
        for name, subset in materialized.groupby(spec.color, dropna=False, sort=False):
            values = dict(zip(subset[spec.x].map(jsonable), subset["value"], strict=False))
            item = {
                "name": jsonable(name),
                "type": series_type,
                "data": [jsonable(values.get(category)) for category in categories],
            }
            if spec.stacked:
                item["stack"] = spec.color
            if spec.kind == "area":
                item["areaStyle"] = {}
            if spec.smooth:
                item["smooth"] = True
            series.append(item)
    else:
        item = {
            "name": spec.y or "count",
            "type": series_type,
            "data": [jsonable(value) for value in materialized["value"]],
        }
        if spec.kind == "area":
            item["areaStyle"] = {}
        if spec.smooth:
            item["smooth"] = True
        series.append(item)
    if spec.annotate:
        for item in series:
            item["label"] = {"show": True, "position": "top"}
    return {
        "tooltip": {"trigger": "axis"},
        "legend": {"show": bool(spec.color)},
        "xAxis": {"type": "category", "data": categories, "name": spec.x},
        "yAxis": {"type": "value", "name": spec.y or "count"},
        "series": series,
    }, materialized


def _histogram(frame: pd.DataFrame, spec: ChartSpec) -> tuple[dict[str, Any], pd.DataFrame]:
    assert spec.x
    values = pd.to_numeric(frame[spec.x], errors="coerce").dropna()
    counts, edges = np.histogram(values, bins=spec.bins, density=spec.density)
    labels = [f"{edges[i]:.3g} to {edges[i + 1]:.3g}" for i in range(len(counts))]
    materialized = pd.DataFrame({"bin": labels, "value": counts})
    return {
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": labels, "name": spec.x},
        "yAxis": {"type": "value", "name": "density" if spec.density else "count"},
        "series": [
            {
                "type": "bar",
                "name": "density" if spec.density else "count",
                "data": counts.tolist(),
            }
        ],
    }, materialized


def _scatter(frame: pd.DataFrame, spec: ChartSpec) -> tuple[dict[str, Any], pd.DataFrame]:
    assert spec.x and spec.y
    columns = [spec.x, spec.y] + [name for name in (spec.size, spec.color) if name]
    materialized = frame[columns].dropna(subset=[spec.x, spec.y]).copy()
    series: list[dict[str, Any]] = []
    groups = (
        materialized.groupby(spec.color, dropna=False, sort=False)
        if spec.color
        else [(spec.title, materialized)]
    )
    for name, subset in groups:
        dimensions = [spec.x, spec.y] + ([spec.size] if spec.size else [])
        series.append(
            {
                "name": jsonable(name),
                "type": "scatter",
                "data": [
                    [jsonable(row[column]) for column in dimensions] for _, row in subset.iterrows()
                ],
                **({"symbolSize": 14} if not spec.size else {}),
            }
        )
    option: dict[str, Any] = {
        "tooltip": {"trigger": "item"},
        "legend": {"show": bool(spec.color)},
        "xAxis": {"type": "value", "name": spec.x},
        "yAxis": {"type": "value", "name": spec.y},
        "series": series,
    }
    if spec.size:
        size_index = 2
        option["visualMap"] = {
            "show": False,
            "dimension": size_index,
            "min": jsonable(materialized[spec.size].min()),
            "max": jsonable(materialized[spec.size].max()),
            "inRange": {"symbolSize": [8, 48]},
        }
    return option, materialized


def _waterfall(frame: pd.DataFrame, spec: ChartSpec) -> tuple[dict[str, Any], pd.DataFrame]:
    assert spec.x and spec.y
    materialized = frame[[spec.x, spec.y]].dropna().copy()
    values = pd.to_numeric(materialized[spec.y])
    base = values.cumsum().shift(fill_value=0)
    base = np.where(values < 0, base + values, base)
    return {
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": materialized[spec.x].map(jsonable).tolist()},
        "yAxis": {"type": "value", "name": spec.y},
        "series": [
            {
                "type": "bar",
                "stack": "waterfall",
                "data": [jsonable(value) for value in base],
                "itemStyle": {"color": "transparent"},
                "silent": True,
            },
            {
                "type": "bar",
                "stack": "waterfall",
                "data": [jsonable(abs(value)) for value in values],
                "itemStyle": {
                    "color": {"type": "linear", "colorStops": [{"offset": 0, "color": "#5470c6"}]}
                },
            },
        ],
    }, materialized


def _combo(frame: pd.DataFrame, spec: ChartSpec) -> tuple[dict[str, Any], pd.DataFrame]:
    assert spec.x and spec.y and spec.y2
    first = _aggregate(frame, [spec.x], spec.y, spec.aggregate).rename(columns={"value": spec.y})
    second = _aggregate(frame, [spec.x], spec.y2, spec.aggregate_y2).rename(
        columns={"value": spec.y2}
    )
    materialized = first.merge(second, on=spec.x, how="outer", sort=False)
    return {
        "tooltip": {"trigger": "axis"},
        "legend": {"data": [spec.y, spec.y2]},
        "xAxis": {"type": "category", "data": materialized[spec.x].map(jsonable).tolist()},
        "yAxis": [{"type": "value", "name": spec.y}, {"type": "value", "name": spec.y2}],
        "series": [
            {"type": "bar", "name": spec.y, "data": materialized[spec.y].map(jsonable).tolist()},
            {
                "type": "line",
                "name": spec.y2,
                "yAxisIndex": 1,
                "data": materialized[spec.y2].map(jsonable).tolist(),
            },
        ],
    }, materialized


def _pie(frame: pd.DataFrame, spec: ChartSpec) -> tuple[dict[str, Any], pd.DataFrame]:
    assert spec.x
    if spec.kind == "sunburst":
        assert spec.color
        materialized = _aggregate(frame, [spec.x, spec.color], spec.y, spec.aggregate)
        children = []
        for parent, subset in materialized.groupby(spec.x, dropna=False, sort=False):
            children.append(
                {
                    "name": jsonable(parent),
                    "children": [
                        {"name": jsonable(row[spec.color]), "value": jsonable(row["value"])}
                        for _, row in subset.iterrows()
                    ],
                }
            )
        return {
            "tooltip": {"trigger": "item"},
            "series": [{"type": "sunburst", "data": children, "radius": ["10%", "90%"]}],
        }, materialized
    materialized = _aggregate(frame, [spec.x], spec.y, spec.aggregate)
    radius: str | list[str] = ["42%", "72%"] if spec.kind == "doughnut" else "68%"
    data = [
        {"name": jsonable(row[spec.x]), "value": jsonable(row["value"])}
        for _, row in materialized.iterrows()
    ]
    return {
        "tooltip": {"trigger": "item"},
        "legend": {"type": "scroll", "orient": "vertical", "right": 0},
        "series": [{"type": "pie", "radius": radius, "data": data}],
    }, materialized


def _kpi(frame: pd.DataFrame, spec: ChartSpec) -> tuple[dict[str, Any], pd.DataFrame]:
    assert spec.y
    if spec.kind == "kpi":
        value = _aggregate(frame, [], spec.y, spec.aggregate)["value"].iloc[0]
        materialized = pd.DataFrame({"value": [value]})
        return {
            "title": {
                "text": spec.title,
                "subtext": f"{jsonable(value)}",
                "left": "center",
                "top": "30%",
                "subtextStyle": {"fontSize": spec.number_font_size, "fontWeight": "bold"},
            },
            "series": [],
        }, materialized
    assert spec.x
    if spec.sampling:
        frequency = {"D": "D", "W": "W", "M": "ME", "Q": "QE", "Y": "YE"}[spec.sampling]
        temporal = frame[[spec.x, spec.y]].copy()
        temporal[spec.x] = pd.to_datetime(temporal[spec.x], errors="coerce")
        temporal = temporal.dropna(subset=[spec.x]).set_index(spec.x)
        method = "nunique" if spec.aggregate == "nunique" else spec.aggregate
        values = (
            temporal[spec.y].resample(frequency).count()
            if method == "count"
            else getattr(temporal[spec.y].resample(frequency), method)()
        )
        materialized = values.rename("value").reset_index()
        materialized["change_percent"] = materialized["value"].pct_change() * 100
        materialized[spec.x] = materialized[spec.x].dt.strftime(spec.date_format)
    else:
        materialized = _aggregate(frame, [spec.x], spec.y, spec.aggregate)
        materialized["change_percent"] = materialized["value"].pct_change() * 100
    current = materialized["value"].iloc[-1] if not materialized.empty else None
    change = materialized["change_percent"].iloc[-1] if not materialized.empty else None
    change_text = "No prior period"
    change_color = "#fac858"
    if isinstance(change, (int, float, np.number)) and pd.notna(change):
        change_text = f"{change:+.2f}% vs prior period"
        change_color = "#91cc75" if change > 0 else "#ee6666" if change < 0 else "#fac858"
    return {
        "title": [
            {"text": spec.title},
            {
                "text": f"{jsonable(current)}",
                "left": "center",
                "top": "22%",
                "textStyle": {"fontSize": spec.number_font_size, "fontWeight": "bold"},
            },
            {
                "text": change_text,
                "left": "center",
                "top": "37%",
                "textStyle": {"fontSize": spec.comparison_font_size, "color": change_color},
            },
        ],
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": materialized[spec.x].map(jsonable).tolist()},
        "yAxis": {"type": "value", "show": False},
        "series": [
            {
                "type": "line",
                "areaStyle": {},
                "data": materialized["value"].map(jsonable).tolist(),
                "itemStyle": {"color": change_color},
            }
        ],
    }, materialized


def _validate_columns(frame: pd.DataFrame, spec: ChartSpec) -> None:
    required = {name for name in (spec.x, spec.y, spec.y2, spec.color, spec.size) if name}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Missing data columns: {', '.join(missing)}")
    if frame.empty:
        raise ValueError("Cannot chart an empty dataset")


def _deep_merge(target: dict[str, Any], source: dict[str, Any]) -> None:
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value
