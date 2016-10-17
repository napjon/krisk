import json
import pytest
import krisk.plot as kk
DATA_DIR = 'krisk/tests/data'
read_option_tests = lambda f: json.load(open(DATA_DIR + '/' + f, 'r'))


def assert_barline_data(plot, true_option, test_legend=True):
    assert plot.option['series'][0] == true_option['series'][0]
    assert plot.option['xAxis']['data'] == true_option['xAxis']['data']
    if test_legend:
        assert plot.option['legend']['data'] == true_option['legend']['data']

def assert_scatter_data(plot, true_option):
    assert plot.option['series'][0]['data'] == true_option['series'][0]['data']
    assert plot.option['xAxis'] == true_option['xAxis']
    assert plot.option['yAxis'] == true_option['yAxis']


def test_bar(gapminder):

    #Bar
    p1 = kk.bar(gapminder,
               'year',
               y='pop',
               c='continent',
               how='mean',
               stacked=True,
               annotate=True)
    opt1 = read_option_tests('bar.json')
    assert_barline_data(p1, opt1)

    #Bar with x-axis and category
    p2 = kk.bar(gapminder,'year',c='continent',stacked=True)
    opt2 = read_option_tests('bar_x_c.json')
    assert_barline_data(p2, opt2)


    # Bar Annotate All
    p3 = kk.bar(gapminder,
               'year',
               y='pop',
               c='continent',
               how='mean',
               stacked=True,
               annotate='all')
    opt3 = read_option_tests('/bar_ann_all.json')
    assert_barline_data(p3, opt3)

    p4 = kk.bar(gapminder,'continent',y='gdpPercap',how='mean')
    opt4 = {'legend': {'data': []},
                             'series': [{'data': [4426.026, 8955.554, 802.675, 3255.367, 19980.596],
                               'name': 'continent',
                               'type': 'bar'}],
                             'title': {'text': ''},
                             'tooltip': {'axisPointer': {'type': ''}},
                             'xAxis': {'data': ['Africa', 'Americas', 'Asia', 'Europe', 'Oceania']},
                             'yAxis': {}}
    assert_barline_data(p4, opt4, test_legend=False) 

def test_trendline(gapminder):

    # p = kk.bar(gapminder,'year',how='mean',y='pop',trendline=True)
    p1 = kk.bar(gapminder,'year',how='mean',y='pop',trendline=True)
    opt1 = read_option_tests('bar_year_pop_mean_trendline.json')

    assert_barline_data(p1, opt1, test_legend=False)
    assert p1.option['series'][-1]['data'] == opt1['series'][-1]['data']
    assert p1.option['series'][-1]['name'] == 'trendline'
    assert p1.option['series'][-1]['type'] == 'line'
    assert p1.option['series'][-1]['lineStyle'] == {'normal': {'color': '#000'}}

    p2 = kk.bar(gapminder,'year',how='mean',y='pop',trendline=True,c='continent',stacked=True)
    opt2 = read_option_tests('bar_year_pop_mean_continent_trendline.json')
    assert_barline_data(p2, opt2)
    assert p2.option['series'][-1]['data'] == opt2['series'][-1]['data']

    try:
        kk.bar(gapminder,'year',how='mean',y='pop',trendline=True,c='continent')
    except AssertionError:
        pass

def test_line(gapminder):
    p = kk.line(
        gapminder,
        'year',
        y='lifeExp',
        c='continent',
        how='mean',
        stacked=True,
        area=True,
        annotate='all')
    opt = read_option_tests('line.json')
    assert_barline_data(p, opt)
    assert p.option['tooltip']['axisPointer']['type'] == 'shadow'
    assert p.option['tooltip']['trigger'] == 'axis'

def test_smooth_line(gapminder):

    p = kk.line(gapminder[gapminder.year == 1952],'continent',y='pop',how='mean',smooth=True)
    assert p.option['series'][0]['smooth'] == True

def test_full_bar_line(gapminder):
    bar = kk.bar(gapminder,'year',c='continent',y='pop',how='mean',stacked=True,full=True,annotate='all')
    line = kk.line(gapminder,'year',c='continent',y='pop',how='mean',stacked=True,full=True,annotate='all')
   
    for i in range(len(bar.option['series'])):
        bar.option['series'][i].pop('type')
        line.option['series'][i].pop('type')

        bar.option['series'][i].pop('label')
        line.option['series'][i].pop('label')

    true_option = read_option_tests('full_bar_line.json')

    assert_barline_data(bar, true_option)
    assert_barline_data(line, true_option)

def test_sort_bar_line(gapminder):
    p = kk.line(gapminder,'year', y='pop', how='mean',c='continent', sort_on='mean', sort_c_on='Americas')

    assert p.option['xAxis']['data'] == [1952, 1957, 1962, 1967, 1972, 1977, 1982, 1987, 1992, 1997, 2002, 2007]
    assert p.option['legend']['data'] == ['Africa', 'Americas', 'Asia', 'Europe', 'Oceania']
    assert p.option['series'][0] == {'data': [-10595881.167,
                                              -9604550.167,
                                              -8874458.167,
                                              -7114907.167,
                                              -5114619.167,
                                              -2722602.167,
                                              158346.833,
                                              3379549.833,
                                              6422966.833,
                                              9196608.833,
                                              11411735.833,
                                              13457809.833],
                                     'name': 'Africa',
                                     'type': 'line'}


def test_hist(gapminder):
    p1 = kk.hist(gapminder,'lifeExp',bins=10)
    opt1  = read_option_tests('hist_x.json')
    assert_barline_data(p1, opt1)
    
    p2 = kk.hist(
        gapminder,
        'lifeExp',
        c='continent',
        bins=20,
        normed=True,
        stacked=True)
    opt2 = read_option_tests('hist.json')
    assert_barline_data(p2, opt2)


def test_density(gapminder):

    p1 = kk.hist(gapminder,'lifeExp',density=True)
    assert p1.option['series'][0]['data'] == [0, 4, 2, 7, 2, 2, 3, 5, 13, 16, 6]
    assert p1.option['series'][-1] == {'data': [0, 4, 2, 7, 2, 2, 3, 5, 13, 16, 6, 0],
                                   'lineStyle': {'normal': {'color': '#000'}},
                                   'name': 'density',
                                   'smooth': True,
                                   'type': 'line'}
    assert p1.option['xAxis']['boundaryGap'] ==  False
    assert p1.option['xAxis']['data'] ==  [0, 28, 34, 39, 44, 49, 55, 60, 65, 70, 75, 81, 0]

    p2 = kk.hist(gapminder,'lifeExp',bins=10,c='continent',stacked=True,density=True)
    opt2 = read_option_tests('hist_lifeExp_b10_continent_density.json')
    assert_barline_data(p2, opt2)

    try:
        kk.hist(gapminder,'year',density=True,c='continent')
    except AssertionError:
        pass



def test_scatter(gapminder):
    # Simple Scatter
    p1 = kk.scatter(gapminder[gapminder.year == 1952],'pop','lifeExp')
    opt1 = read_option_tests('simple_scatter.json')
    assert_scatter_data(p1, opt1)
    assert p1.option['title'] ==  {'text': ''}
    assert p1.option['tooltip'] == {'axisPointer': {'type': 'line'},
                                     'fontFamily': 'sans-serif',
                                     'fontSize': 14,
                                     'fontStyle': 'normal',
                                     'trigger': 'item',
                                     'triggerOn': 'mousemove'}

    # Grouped Scatter
    p2 = kk.scatter(
        gapminder[gapminder.year == 1952],
        'lifeExp',
        'gdpPercap',
        s='pop',
        c='continent')
    opt2 = read_option_tests('scatter.json')
    assert_scatter_data(p2, opt2)
    assert p2.option['series'][0]['name'] ==  'Africa'
    assert p2.option['series'][0]['type'] ==  'scatter'
    assert p2.option['visualMap'][0] ==  opt2['visualMap'][0]

    # Scatter
    
    p3 = kk.scatter(gapminder[gapminder.year == 1952], 'lifeExp', 'gdpPercap', s='pop')
    opt3 = read_option_tests('scatter_single.json')
    assert_scatter_data(p3, opt3)
