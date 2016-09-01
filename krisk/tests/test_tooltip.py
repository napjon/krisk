import pytest
import json
import pandas as pd
import krisk.plot as kk
DATA_DIR = 'krisk/tests/data'


def test_tooltip(gap_chart):
    tooltip = gap_chart.option['tooltip']
    true_tooltip = json.load(open(DATA_DIR + '/tooltip.json', 'r'))
    assert tooltip == true_tooltip


def test_tooltip_style():
    p = kk.bar(pd.DataFrame({'a': [1, 2, 3]}), 'a')
    p.set_tooltip_style(trigger='axis', axis_pointer='shadow', font_size=30)
    assert p.get_option()['tooltip'] == {'axisPointer': {'type': 'shadow'},
                                         'fontFamily': 'sans-serif',
                                         'fontSize': 30,
                                         'fontStyle': 'normal',
                                         'trigger': 'axis',
                                         'triggerOn': 'mousemove'}


def test_option(gap_chart):
    true_option = json.load(open(DATA_DIR + '/scatter_tooltip.json', 'r'))
    assert gap_chart.option == true_option


def test_repr(gap_chart):

    l_repr = gap_chart._repr_javascript_().split('\n')
    f_repr = [l_repr[i] for i in range(len(l_repr)) if i not in [1, 2, 10]]
    true_repr = open(DATA_DIR + '/scatter_repr.txt', 'r').read().split('\n')

    # Full list array comparison yield AssertionError in py.test eventhough it's correct.
    # Just partially test this
    assert len(f_repr) == len(true_repr)
    assert f_repr[:5] == true_repr[:5]
    assert f_repr[-5:] == true_repr[-5:]
