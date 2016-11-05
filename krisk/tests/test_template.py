import pytest
import json
ECHARTS_VERSION = '3.2.1'


def test_html():
    from krisk.chart.api import Chart

    c = Chart()
    c.to_html('../sample.html')

    sample = open('../sample.html', 'r').read().split('\n')
    template = open('krisk/static/template.html').read().split('\n')

    assert sample[:20] == template[:20]


def test_init_nb():
    from krisk.util import init_notebook

    js_data = init_notebook().data
    js_init_template = """
    require.config({{
                 baseUrl : "https://cdn.rawgit.com/napjon/krisk/master/krisk/static",
                 paths: {{
                      echarts: "https://cdnjs.cloudflare.com/ajax/libs/echarts/{VER}/echarts.min"
                  }}
    }});
    """
    assert js_init_template.format(VER=ECHARTS_VERSION) == js_data
