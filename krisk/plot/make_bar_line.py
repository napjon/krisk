from copy import deepcopy

import numpy as np
import pandas as pd

from krisk.plot.make_chart import insert_series_data, round_list
from krisk.util import future_warning

d_annotate = {'normal': {'show': True, 'position': 'top'}}


def set_full_style_condition(chart, data, c, **kwargs):

    if kwargs['full']:
        if kwargs['stacked']:
            if c:
                data = data.div(data.sum(1), axis=0)
            chart.option['yAxis']['max'] = 1
        else:
            raise ValueError("For full to worked, stacked must be set to True")

    return data


def set_bar_line_chart(chart, df, x, c, **kwargs):
    """Construct Bar, Line, and Histogram"""

    data = None
    chart_type = kwargs['type']

    if chart_type in ['bar', 'line']:
        data = get_bar_or_line_data(df, x, c, **kwargs)
        chart.option['xAxis']['data'] = data.index.values.tolist()
    elif chart_type == 'hist':
        chart_type = 'bar'
        data, bins = get_hist_data(df, x, c, **kwargs)
        chart.option['xAxis']['data'] = bins
    elif chart_type == 'bar_line':
        data = set_barline(df, x, chart, **kwargs)
        chart.option['xAxis']['data'] = data.index.values.tolist()
        return
    elif chart_type in ['bar_tidy', 'line_tidy']:
        chart_type = chart_type.replace('_tidy', '')
        data = df
        chart.option['xAxis']['data'] = data.index.astype(str).tolist()

    if chart_type in ['bar', 'line'] and kwargs['type'] != 'hist':
        data = set_full_style_condition(chart, data, c, **kwargs)

    if c:
        # append data for every category
        for cat in data.columns:
            insert_series_data(data[cat], x, chart_type, chart, cat)
    else:
        insert_series_data(data, x, chart_type, chart)

    series = chart.option['series']

    ########Provide stacked,annotate, area for bar line hist#################
    if c and kwargs['stacked']:
        for s in series:
            s['stack'] = c

            if chart_type == 'line' and kwargs['area']:
                s['areaStyle'] = {'normal': {}}

            if kwargs['annotate'] == 'all':
                s['label'] = deepcopy(d_annotate)

                if chart_type == 'bar':
                    s['label']['normal']['position'] = 'inside'

    if kwargs['annotate'] == 'top':
        series[-1]['label'] = d_annotate
    # TODO: make annotate receive all kinds supported in echarts.

    # Add Custom Styling
    if kwargs['type'] == 'hist':
        histogram_custom_style(chart, data, c, series, **kwargs)
    elif chart_type == 'bar':
        bar_custom_style(c, series, **kwargs)
    elif chart_type == 'line':
        line_custom_style(series, **kwargs)


def bar_custom_style(c, series, **kwargs):
    # Special Bar Condition: Trendline
    if kwargs['trendline']:
        trendline = {'name': 'trendline', 'type': 'line',
                     'lineStyle': {'normal': {'color': '#000'}}}

        if c and kwargs['stacked']:
            trendline['data'] = [0] * len(series[-1]['data'])
            trendline['stack'] = c
        elif c is None:
            trendline['data'] = series[0]['data']
        else:
            raise ValueError('Trendline must either stacked category,'
                                 ' or not category')
        series.append(trendline)


def line_custom_style(series, **kwargs):
    # Special Line Condition: Smooth
    if kwargs['smooth']:
        for s in series:
            s['smooth'] = True


def histogram_custom_style(chart, data, c, series, **kwargs):
    # Special Histogram Condition: Density
    #TODO NEED IMPROVEMENT!
    if kwargs['type'] == 'hist' and kwargs['density']:
        
        density = {'name':'density', 'type': 'line', 'smooth': True,
                   'lineStyle': {'normal': {'color': '#000'}}}
        chart.option['xAxis']['boundaryGap'] = False

        # The density have to be closed at zero. So all of xAxis and series
        # must be updated to incorporate the changes
        chart.option['xAxis']['data'] = [0] + chart.option['xAxis']['data'] + [0]

        for s in series:
            s['data'] = [0] + s['data']

        if c and kwargs['stacked']:
            density['data'] = [0] + round_list(data.sum(axis=1)) + [0]
        elif c is None:
            density['data'] = [0] + round_list(data) + [0]
        else:
            raise ValueError('Density must either stacked category, '
                                 'or not category')

        series.append(density)   


def get_bar_or_line_data(df, x, c, y, **kwargs):
    """Get Bar and Line manipulated data"""
    
    if c and y:
        data = df.pivot_table(
                index=x,
                values=y,
                columns=c,
                aggfunc=kwargs['how'],
                fill_value=None)
    elif c and y is None:
        data = pd.crosstab(df[x], df[c])
    elif c is None and y:
        data = df.groupby(x)[y].agg(kwargs['how'])
    else:
        data = df[x].value_counts()

    # Specify sort_on and order method
    sort_on = kwargs['sort_on']
    descr_keys = pd.Series([0]).describe().keys().tolist()
    
    if isinstance(sort_on, str):
        assert sort_on in ['index','values'] + descr_keys

    if sort_on == 'index':
        data.sort_index(inplace=True, ascending=kwargs['ascending'])
    else:
        if sort_on != 'values':
            val_deviation = sort_on(data) if callable(sort_on) else sort_on
            data = data - val_deviation
        if c:
            assert kwargs['sort_c_on'] is not None
            (data.sort_values(kwargs['sort_c_on'],
                              inplace=True,
                              ascending=kwargs['ascending']))
        else:
            data.sort_values(inplace=True, ascending=kwargs['ascending'])

    return data


def get_hist_data(df, x, c, **kwargs):
    """Get Histogram manipulated data"""

    y_val, x_val = np.histogram(
        df[x], bins=kwargs['bins'], normed=kwargs['normed'])
    bins = x_val.astype(int).tolist()

    if c:
        data = pd.DataFrame()
        for cat, sub in df.groupby(c):
            data[cat] = (pd.cut(sub[x], x_val).value_counts(
                sort=False, normalize=kwargs['normed']))
    else:
        data = pd.Series(y_val)

    return data, bins


def set_barline(chart, df, x, **kwargs):
    """Set Bar-Line charts"""

    ybar = kwargs['ybar']
    yline = kwargs['yline']

    if kwargs['is_distinct'] is True:
        data = df[[x, ybar, yline]].drop_duplicates(subset=[x]).copy()
        data.index = data.pop(x)
    else:
        data = (df
                .groupby(x)
                .agg({ybar: kwargs['bar_aggfunc'],
                      yline: kwargs['line_aggfunc']}))

        if kwargs['sort_on'] == 'index':
            data.sort_index(ascending=kwargs['ascending'], inplace=True)
        else:
            data.sort_values(kwargs[kwargs['sort_on']],
                             ascending=kwargs['ascending'], inplace=True)

    def get_series(col, type): return dict(name=col, type=type,
                                           data=round_list(data[col]))
    chart.option['series'] = [
        get_series(ybar, 'bar'),
        dict(yAxisIndex=1, **get_series(yline, 'line'))
    ]

    if kwargs['hide_split_line'] is True:
        def get_yaxis(col): return {'name': col, 'splitLine': {'show': False}}
        chart.option['yAxis'] = [get_yaxis(ybar), get_yaxis(yline)]

    if kwargs['style_tooltip'] is True:
        chart.set_tooltip_style(axis_pointer='shadow', trigger='axis')

    chart.option['xAxis']['data'] = data.index.values.tolist()
    return data


def set_waterfall(chart, s, **kwargs):

    # TODO
    # * Find a way to naming index and value

    invisible_bar = {'name': '',
                     'type': 'bar',
                     'stack': 'stack',
                     "itemStyle": {
                         "normal": {
                             "barBorderColor": 'rgba(0,0,0,0)',
                             "color": 'rgba(0,0,0,0)'
                         },
                         "emphasis": {
                             "barBorderColor": 'rgba(0,0,0,0)',
                             "color": 'rgba(0,0,0,0)'
                         }
                     }}
    visible_bar = {'type': 'bar', 'stack': 'stack'}

    invisible_series = s.cumsum().shift(1).fillna(0)

    if (invisible_series >= 0).all() is np.False_:
        raise NotImplementedError("cumulative sum should be positive")

    invisible_series = np.where(s < 0,
                                invisible_series - s.abs(),
                                invisible_series)
    invisible_bar['data'] = invisible_series.round(3).tolist()
    chart.option['series'].append(invisible_bar)

    def add_bar(series, name):
        """Append bar to chart series"""

        bar = deepcopy(visible_bar)
        bar['name'] = name
        bar['data'] = series.values.tolist()
        chart.option['series'].append(bar)

    def add_annotate(bar_series, position):
        bar_series['label'] = deepcopy(d_annotate)
        bar_series['label']['normal']['position'] = position

    if kwargs['color_coded']:

        boolean_pivot = (pd.DataFrame(s)
                         .pivot_table(values=s.name,
                                      index=s.index,
                                      columns=s > 0)
                         .abs()
                         .round(3)
                         .fillna('-'))

        add_bar(boolean_pivot[True], kwargs['up_name'])
        add_bar(boolean_pivot[False], kwargs['down_name'])

        chart.option['legend']['data'] = [kwargs['up_name'],
                                          kwargs['down_name']]
    else:
        add_bar(s.abs().round(3), s.name)

    if kwargs['annotate']:
        if kwargs['annotate'] == 'inside':
            for bar_series in chart.option['series']:
                add_annotate(bar_series, kwargs['annotate'])
        else:
            add_annotate(chart.option['series'][1], "top")
            if kwargs['color_coded']:
                add_annotate(chart.option['series'][2], "bottom")

    chart.option['xAxis']['data'] = s.index.values.tolist()
    chart.set_tooltip_style(trigger='axis', axis_pointer='shadow')

    chart.option['tooltip']['formatter'] = """function (params) {
            var tar;
            if (params[1].value != '-') {
                tar = params[1];
            }
            else {
                tar = params[2];
            }
            return tar.name + '<br/>' + tar.seriesName + ' : ' + tar.value;
        }"""

    return s
