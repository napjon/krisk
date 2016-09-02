import json
import pytest
import krisk.plot as kk
DATA_DIR = 'krisk/tests/data'


def test_bar(gapminder):

    #Bar
    true_option = json.load(open(DATA_DIR + '/bar.json', 'r'))
    p = kk.bar(gapminder,
               'year',
               y='pop',
               c='continent',
               how='mean',
               stacked=True,
               annotate=True)
    assert p.get_option() == true_option

    # Bar Annotate All
    true_option = json.load(open(DATA_DIR + '/bar_ann_all.json', 'r'))
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



def test_line(gapminder):

    true_option = json.load(open(DATA_DIR + '/line.json', 'r'))
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


def test_hist(gapminder):

    true_option = json.load(open(DATA_DIR + '/hist.json', 'r'))
    p = kk.hist(
        gapminder,
        'lifeExp',
        c='continent',
        bins=20,
        normed=True,
        stacked=True)

    assert p.get_option() == true_option


def test_scatter(gapminder):

    # Grouped Scatter
    true_option = json.load(open(DATA_DIR + '/scatter.json', 'r'))
    p = kk.scatter(
        gapminder[gapminder.year == 1952],
        'lifeExp',
        'gdpPercap',
        s='pop',
        c='continent')
    assert p.get_option() == true_option

    # Scatter
    true_option = json.load(open(DATA_DIR + '/scatter_single.json', 'r'))
    p = kk.scatter(
        gapminder[gapminder.year == 1952], 'lifeExp', 'gdpPercap', s='pop')
    assert p.get_option() == true_option
