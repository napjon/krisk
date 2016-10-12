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
               category='continent',
               how='mean',
               stacked=True,
               annotate=True)
    assert p.get_option() == true_option

    # Bar Annotate All
    true_option = json.load(open(DATA_DIR + '/bar_ann_all.json', 'r'))
    p = kk.bar(gapminder,
               'year',
               y='pop',
               category='continent',
               how='mean',
               stacked=True,
               annotate='all')
    assert p.get_option() == true_option


def test_line(gapminder):

    true_option = json.load(open(DATA_DIR + '/line.json', 'r'))
    p = kk.line(
        gapminder,
        'year',
        y='lifeExp',
        category='continent',
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
        category='continent',
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
        size='pop',
        category='continent')
    assert p.get_option() == true_option

    # Scatter
    true_option = json.load(open(DATA_DIR + '/scatter_single.json', 'r'))
    p = kk.scatter(
        gapminder[gapminder.year == 1952], 'lifeExp', 'gdpPercap', size='pop')
    assert p.get_option() == true_option
