import pytest
import pandas as pd
import krisk.plot as kk

DATA_DIR = "krisk/tests/data"


@pytest.fixture(scope="module")
def df_simple():
    return pd.DataFrame({'x': ['a', 'b', 'c']})


@pytest.fixture(scope="module")
def bar_simple(df_simple):
    return kk.bar(df_simple, 'x')


@pytest.fixture(scope="module")
def gapminder():
    return (pd.read_csv(
        DATA_DIR + '/gapminderDataFiveYear.txt', sep='\t').groupby(
            ['year', 'continent'], as_index=False).first())

@pytest.fixture(scope="module")
def decl_chart():
    "Declarative Chart"
    from krisk.chart.api import Chart
    chart = Chart()
    chart.option['series'] = [{'data': [10, 3, 7, 4, 5], 'name': 'continent', 'type': 'bar'}]
    chart.option['xAxis'] =  {'data': ['Americas', 'Asia', 'Africa', 'Oceania', 'Europe']}
    return chart

@pytest.fixture
def gap_chart(gapminder):
    p = kk.scatter(
        gapminder[gapminder.year == 2007],
        'lifeExp',
        'gdpPercap',
        s='pop',
        c='continent')
    p.set_size(width=1000, height=500)
    p.set_tooltip_format(
        ['country', 'lifeExp', 'gdpPercap', 'pop', 'continent'])
    p.set_theme('dark')
    p.set_toolbox(save_format='png', restore=True, data_zoom=True)
    p.set_legend(orient='vertical', x_pos='-1%', y_pos='-3%')
    chart = p.set_title('GapMinder of 2007', x_pos='center', y_pos='-5%')
    return chart
