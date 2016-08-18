import pytest

@pytest.fixture
def chart_gapminder():
    import pandas as pd
    import krisk.plot as kk
    df = pd.read_csv('data/gapminderDataFiveYear.txt', sep='\t')
    return (kk.line(df,x='year',category='continent',y='lifeExp',how='mean',area=True,stacked=True)
             .set_theme('vintage'))


def test_option(chart_gapminder):
    import json
    json_path ='data/json_gapminder_line_year_continent_lifeExp_mean_area_stacked.json'
    option = json.load(open(json_path,'r'))
    assert option == chart_gapminder._option
    