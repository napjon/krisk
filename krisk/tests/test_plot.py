import json
import pytest
import krisk.plot as kk
DATA_DIR = 'krisk/tests/data'

read_option_tests = lambda f: json.load(open(DATA_DIR + '/' + f, 'r'))

def test_bar(gapminder):

    #Bar
    true_option = read_option_tests('bar.json')
    p = kk.bar(gapminder,
               'year',
               y='pop',
               c='continent',
               how='mean',
               stacked=True,
               annotate=True)
    assert p.get_option() == true_option

    #Bar with x-axis and category
    true_option = read_option_tests('bar_x_c.json')
    p = kk.bar(gapminder,'year',c='continent',stacked=True)
    assert p.get_option() == true_option


    # Bar Annotate All
    true_option = read_option_tests('/bar_ann_all.json')
    p = kk.bar(gapminder,
               'year',
               y='pop',
               c='continent',
               how='mean',
               stacked=True,
               annotate='all')
    assert p.get_option() == true_option

    p = kk.bar(gapminder,'continent',y='gdpPercap',how='mean')
    assert p.get_option() == {'legend': {'data': []},
                             'series': [{'data': [4426.026, 8955.554, 802.675, 3255.367, 19980.596],
                               'name': 'continent',
                               'type': 'bar'}],
                             'title': {'text': ''},
                             'tooltip': {'axisPointer': {'type': ''}},
                             'xAxis': {'data': ['Africa', 'Americas', 'Asia', 'Europe', 'Oceania']},
                             'yAxis': {}}

def test_trendline(gapminder):

    p = kk.bar(gapminder,'year',how='mean',y='pop',trendline=True)
    assert p.get_option() == read_option_tests('bar_year_pop_mean_trendline.json')

    p = kk.bar(gapminder,'year',how='mean',y='pop',trendline=True,c='continent',stacked=True)
    assert p.get_option() == read_option_tests('bar_year_pop_mean_continent_trendline.json')

    try:
        kk.bar(gapminder,'year',how='mean',y='pop',trendline=True,c='continent')
    except AssertionError:
        pass

def test_line(gapminder):

    true_option = read_option_tests('line.json')
    p = kk.line(
        gapminder,
        'year',
        y='lifeExp',
        c='continent',
        how='mean',
        stacked=True,
        area=True,
        annotate='all')

    assert p.get_option() == true_option

def test_smooth_line(gapminder):

    p = kk.line(gapminder[gapminder.year == 1952],'continent',y='pop',how='mean',smooth=True)
    assert p.get_option()['series'][0]['smooth'] == True

def test_full_bar_line(gapminder):
    bar = kk.bar(gapminder,'year',c='continent',y='pop',how='mean',stacked=True,full=True,annotate='all')
    line = kk.line(gapminder,'year',c='continent',y='pop',how='mean',stacked=True,full=True,annotate='all')
   
    for i in range(len(bar.option['series'])):
            bar.option['series'][i].pop('type')
            line.option['series'][i].pop('type')

            bar.option['series'][i].pop('label')
            line.option['series'][i].pop('label')

    true_option = read_option_tests('full_bar_line.json')

    assert bar.option == line.option == true_option


def test_hist(gapminder):

    true_option  = read_option_tests('hist_x.json')
    p = kk.hist(gapminder,'lifeExp',bins=10)
    assert p.get_option() == true_option


    true_option = read_option_tests('hist.json')
    p = kk.hist(
        gapminder,
        'lifeExp',
        c='continent',
        bins=20,
        normed=True,
        stacked=True)

    assert p.get_option() == true_option


def test_density(gapminder):

    option = kk.hist(gapminder,'lifeExp',density=True).get_option()

    assert option['series'][0]['data'] == [0, 4, 2, 7, 2, 2, 3, 5, 13, 16, 6]
    assert option['series'][-1] == {'data': [0, 4, 2, 7, 2, 2, 3, 5, 13, 16, 6, 0],
                                   'lineStyle': {'normal': {'color': '#000'}},
                                   'name': 'density',
                                   'smooth': True,
                                   'type': 'line'}
    assert option['xAxis'] == {'boundaryGap': False,
                               'data': [0, 28, 34, 39, 44, 49, 55, 60, 65, 70, 75, 81, 0]}

    true_option = read_option_tests('hist_lifeExp_b10_continent_density.json')
    option2 = kk.hist(gapminder,'lifeExp',bins=10,c='continent',stacked=True,density=True).get_option()
    assert true_option == option2

    try:
        kk.hist(gapminder,'year',density=True,c='continent')
    except AssertionError:
        pass



def test_scatter(gapminder):
    # Simple Scatter
    p = kk.scatter(gapminder[gapminder.year == 1952],'pop','lifeExp')
    true_option = read_option_tests('simple_scatter.json')
    assert p.get_option() == true_option

    # Grouped Scatter
    true_option = read_option_tests('scatter.json')
    p = kk.scatter(
        gapminder[gapminder.year == 1952],
        'lifeExp',
        'gdpPercap',
        s='pop',
        c='continent')
    assert p.get_option() == true_option

    # Scatter
    true_option = read_option_tests('scatter_single.json')
    p = kk.scatter(
        gapminder[gapminder.year == 1952], 'lifeExp', 'gdpPercap', s='pop')
    assert p.get_option() == true_option
