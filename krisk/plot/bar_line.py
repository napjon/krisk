from copy import deepcopy
import numpy as np
import pandas as pd

from krisk.plot.make_chart import insert_series_data, round_list


def set_bar_line_chart(chart, df, x, c, **kwargs):
    """Construct Bar, Line, and Histogram"""

    data = None
    chart_type = kwargs['type']

    if chart_type in ['bar', 'line']:
        data = get_bar_line_data(df, x, c, **kwargs)
        chart.option['xAxis']['data'] = data.index.values.tolist()

    elif chart_type == 'hist':
        chart_type = 'bar'
        data, bins = get_hist_data(df, x, c, **kwargs)
        chart.option['xAxis']['data'] = bins

    if c:
        # append data for every category
        for cat in data.columns:
            insert_series_data(data[cat], x, chart_type, chart, cat)
    else:
        insert_series_data(data, x, chart_type, chart)

    series = chart.option['series']

    ########Provide stacked,annotate, area for bar line hist#################
    d_annotate = {'normal': {'show': True, 'position': 'top'}}

    if c and kwargs['stacked']:
        for s in series:
            s['stack'] = c

            if chart_type == 'line' and kwargs['area']:
                s['areaStyle'] = {'normal': {}}

            if kwargs['annotate'] == 'all':
                s['label'] = deepcopy(d_annotate)

                if chart_type == 'bar':
                    s['label']['normal']['position'] = 'inside'

        if kwargs['type'] in ['line','bar'] and kwargs['full']:
            chart.option['yAxis']['max'] = 1

    if kwargs['annotate'] == 'top':
        series[-1]['label'] = d_annotate
     # TODO: make annotate receive all kinds supported in echarts.

    # Special Bar Condition: Trendline
    if kwargs['type'] == 'bar' and kwargs['trendline']:
        trendline = {'name':'trendline', 'type': 'line',
                     'lineStyle': {'normal': {'color': '#000'}}}

        if c and kwargs['stacked']:
            trendline['data']  =  [0] * len(series[-1]['data'])
            trendline['stack'] = c
        elif c is None:
            trendline['data'] = series[0]['data']
        else:
            raise AssertionError('Trendline must either stacked category, or not category')

        series.append(trendline)

    # Special Line Condition: Smooth
    if kwargs['type'] == 'line' and kwargs['smooth']:
        for s in series:
            s['smooth'] = True


    # Special Histogram Condition: Density
    #TODO NEED IMPROVEMENT!
    if kwargs['type'] == 'hist' and kwargs['density']:
        
        density = {'name':'density', 'type': 'line', 'smooth': True,
                   'lineStyle': {'normal': {'color': '#000'}}}
        chart.option['xAxis']['boundaryGap'] = False

        # The density have to be closed at zero. So all of xAxis and series must be updated
        # To incorporate the changes
        chart.option['xAxis']['data'] = [0] + chart.option['xAxis']['data'] + [0]

        for s in series:
            s['data'] = [0] + s['data']

        if c and kwargs['stacked']:
            density['data'] = [0] + round_list(data.sum(axis=1)) + [0]
        elif c is None:
            density['data'] =  [0] + round_list(data) + [0] 
        else:
            raise AssertionError('Density must either stacked category, or not category')

        series.append(density)   


def get_bar_line_data(df, x, c, y, **kwargs):
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

    #Specify sort_on and order method
    sort_on = kwargs['sort_on']
    descr_keys = pd.Series([0]).describe().keys().tolist()
    
    if isinstance(sort_on, str):
        assert sort_on in ['index','values'] + descr_keys

    if sort_on == 'index':
        data.sort_index(inplace=True, ascending=kwargs['ascending'])
    else:
        if sort_on != 'values':
            val_deviation = data.describe().loc[sort_on] if isinstance(sort_on, str) else sort_on
            data = data - val_deviation
        if c:
            assert kwargs['sort_c_on'] is not None
            data.sort_values(kwargs['sort_c_on'], inplace=True, ascending=kwargs['ascending'])
        else:
            data.sort_values(inplace=True, ascending=kwargs['ascending'])

    # Stacked when category
    if c and kwargs['stacked'] and kwargs['full']:
        data = data.div(data.sum(1),axis=0)

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
