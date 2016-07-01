

df = pd.read_csv('gapminderDataFiveYear.txt',sep='\t')

def test_bar():
    
    true_option = json.load(open('pandas-echarts/tests/data/bar_option.json','r'))
    p = bar(df,'lifeExp',y='pop',category='continent',how='mean',stacked=True)
    
    assert p._option == true_option
    
def test_line():
    
    true_option = json.load(open('pandas-echarts/tests/data/line_option.json','r'))
    p = line(df,'year',y='lifeExp',category='continent',how='mean',stacked=True,area=True)
    
    assert p._option == true_option
    
def test_hist():
    
    true_option = json.load(open('pandas-echarts/tests/data/hist_option.json','r'))
    p = hist(df,'lifeExp',category='continent',bins=100,normed=True,stacked=True)
    
    assert p._option == true_option
    
def test_scatter():
    
    true_option = json.load(open('pandas-echarts/tests/data/scatter_option.json','r'))
    p = scatter(df[df.year == 1952],'lifeExp','gdpPercap',size='pop',category='continent')
    
    assert p._option == true_option

test_bar()
test_line()
test_hist()
test_scatter()