def test_html(tmp_path):
    from krisk.chart.api import Chart

    c = Chart()
    output = tmp_path / "sample.html"
    c.to_html(output)
    sample = output.read_text()
    assert "echarts.init" in sample
    assert "requirejs" not in sample.lower()


def test_init_nb():
    from krisk.util import init_notebook

    js_data = init_notebook().data
    assert js_data == "/* Krisk 0.9+ charts are self-contained. */"
    assert "http" not in js_data
