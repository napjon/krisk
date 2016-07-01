import pytest

@pytest.fixture
def chart_gapminder():
    import pandas as pd
    from krisk import make_chart
    df = pd.read_csv('../echarts/gapminderDataFiveYear.txt')
    return (line(df,x='year',category='continent',y='lifeExp',how='mean',area=True,stacked=True)
             .set_theme('vintage')
             .set_tooltip())


def test_option(chart_gapminder):
    import json
    json_path ='krisk/tests/json_gapminder_line_year_continent_lifeExp_mean_area_stacked.json'
    option = json.load(json_path,'r')
    assert option == chart_gapminder._option
    