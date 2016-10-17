import pytest
import json
import pandas as pd
import krisk.plot as kk
DATA_DIR = 'krisk/tests/data'


def test_tooltip(gap_chart):
    formatter = gap_chart.option['tooltip']['formatter']
    true_formatter = json.load(open(DATA_DIR + '/tooltip.json', 'r'))['formatter']
    assert formatter == true_formatter


def test_tooltip_style(decl_chart):
    template_tooltip = decl_chart.option['tooltip']
    assert template_tooltip == {'axisPointer': {'type': 'line'},
                                 'fontFamily': 'sans-serif',
                                 'fontSize': 14,
                                 'fontStyle': 'normal',
                                 'trigger': 'item',
                                 'triggerOn': 'mousemove'}

    decl_chart.set_tooltip_style(trigger='axis',axis_pointer='shadow',font_size=20)
    tooltip = decl_chart.option['tooltip']
    assert tooltip == {'axisPointer': {'type': 'shadow'},
                     'fontFamily': 'sans-serif',
                     'fontSize': 20,
                     'fontStyle': 'normal',
                     'trigger': 'axis',
                     'triggerOn': 'mousemove'}
