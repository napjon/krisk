
import json
import pytest
import krisk.plot as kk

@pytest.fixture
def df():
    import pandas as pd
    return (pd.read_csv('data/gapminderDataFiveYear.txt',sep='\t')
          .groupby(['year','continent'],as_index=False).first())

def test_bar(df):
    
    true_option = json.load(open('data/bar.json','r'))
    p = kk.bar(df,'lifeExp',y='pop',category='continent',how='mean',stacked=True)
    
    assert p._option == true_option
    
def test_line(df):
    
    true_option = json.load(open('data/line.json','r'))
    p = kk.line(df,'year',y='lifeExp',category='continent',how='mean',stacked=True,area=True)
    
    assert p._option == true_option
    
def test_hist(df):
    
    true_option = json.load(open('data/hist.json','r'))
    p = kk.hist(df,'lifeExp',category='continent',bins=100,normed=True,stacked=True)
    
    assert p._option == true_option
    
def test_scatter(df):
    
    true_option = json.load(open('data/scatter.json','r'))
    p = kk.scatter(df[df.year == 1952],'lifeExp','gdpPercap',size='pop',category='continent')
    
    assert p._option == true_option