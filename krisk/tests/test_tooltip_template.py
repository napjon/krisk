import pytest
import json

@pytest.fixture
def chart():
    import pandas as pd    
    import krisk.plot as kk
    
    df = (pd.read_csv('krisk/krisk/tests/data/gapminderDataFiveYear.txt',sep='\t')
          .groupby(['year','continent'],as_index=False).first())

    p = kk.scatter(df[df.year == 2007],'lifeExp','gdpPercap',size='pop',category='continent')
    p.set_size(width=1000, height=500)
    p.set_tooltip_format(['country','lifeExp','gdpPercap','pop','continent'])
    p.set_theme('dark')
    p.set_toolbox(save_format='png',restore=True,data_zoom=True)
    p.set_legend(orient='vertical',x_pos='-1%',y_pos='-3%')
    chart = p.set_title('GapMinder of 2007',x_pos='center',y_pos='-5%')
    return chart

def test_tooltip(chart):
    tooltip = chart._option['tooltip']
    true_tooltip = json.load(open('data/tooltip.json','r'))
    assert tooltip == true_tooltip
    
def test_option():
    true_option = json.load(open('data/scatter_tooltip.json','r'))
    assert chart._option == true_option

def test_repr():
    pass