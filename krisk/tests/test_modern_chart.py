import json

import pandas as pd
import pytest

from krisk import Chart, ChartSpec, plot


@pytest.fixture
def sales():
    return pd.DataFrame(
        {
            "month": ["Jan", "Jan", "Feb", "Feb"],
            "segment": ["A", "B", "A", "B"],
            "revenue": [10, 20, 30, 40],
            "orders": [1, 2, 3, 4],
        }
    )


@pytest.mark.parametrize(
    ("kind", "values"),
    [
        ("bar", {"x": "month", "y": "revenue", "aggregate": "sum"}),
        ("line", {"x": "month", "y": "revenue", "aggregate": "mean"}),
        ("area", {"x": "month", "y": "revenue", "aggregate": "sum"}),
        ("histogram", {"x": "revenue"}),
        ("scatter", {"x": "orders", "y": "revenue", "color": "segment"}),
        ("waterfall", {"x": "month", "y": "revenue"}),
        ("combo", {"x": "month", "y": "revenue", "y2": "orders"}),
        ("pie", {"x": "segment", "y": "revenue", "aggregate": "sum"}),
        ("doughnut", {"x": "segment", "y": "revenue", "aggregate": "sum"}),
        ("sunburst", {"x": "month", "color": "segment", "y": "revenue", "aggregate": "sum"}),
        ("kpi", {"y": "revenue", "aggregate": "sum"}),
        ("kpi_trend", {"x": "month", "y": "revenue", "aggregate": "sum"}),
    ],
)
def test_every_chart_kind_compiles(sales, kind, values):
    chart = Chart.from_dataframe(sales, ChartSpec(kind=kind, **values))
    assert "series" in chart.option
    json.dumps(chart.option)
    assert chart.snapshot_data is not None


def test_jupyter_bundle_and_self_contained_html(sales, tmp_path):
    chart = Chart.from_dataframe(sales, ChartSpec(kind="bar", x="month", y="revenue"))
    bundle = chart._repr_mimebundle_()
    assert "text/html" in bundle
    assert "application/vnd.krisk.chart+json" in bundle
    output = tmp_path / "chart.html"
    chart.to_html(output)
    content = output.read_text()
    assert "echarts.init" in content
    assert "cdn" not in content.lower()
    assert "requirejs" not in content.lower()
    assert "View chart data as a table" in content
    assert "<table" in content


def test_typed_categories_preserve_source_order():
    frame = pd.DataFrame({"month": ["Jan", "Feb", "Mar"], "revenue": [1, 2, 3]})
    chart = Chart.from_dataframe(
        frame, ChartSpec(kind="line", x="month", y="revenue", aggregate="sum")
    )
    assert chart.option["xAxis"]["data"] == ["Jan", "Feb", "Mar"]


def test_typed_histogram_supports_density(sales):
    chart = Chart.from_dataframe(
        sales,
        ChartSpec(kind="histogram", x="revenue", bins=2, density=True),
    )
    assert chart.option["yAxis"]["name"] == "density"
    assert chart.option["series"][0]["name"] == "density"


def test_rejects_executable_override():
    with pytest.raises(ValueError, match="Executable JavaScript"):
        ChartSpec(
            kind="bar",
            x="month",
            safe_overrides={"tooltip": {"formatter": "function () { return 1 }"}},
        )


def test_chartics_number_overtime_compatibility():
    frame = pd.DataFrame(
        {"date": ["2026-01-01", "2026-01-02", "2026-01-03"], "orders": [10, 15, 30]}
    )
    chart = plot.number(
        frame,
        "date",
        "orders",
        overtime=True,
        how="sum",
        sampling="D",
        num_font_size=52,
        period_font_size=16,
    )
    assert chart.option["title"][1]["text"] == "30"
    assert chart.option["title"][1]["textStyle"]["fontSize"] == 52
    assert chart.option["title"][2]["text"].startswith("+100.00%")
