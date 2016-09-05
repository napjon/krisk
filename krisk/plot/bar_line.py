from copy import deepcopy
import numpy as np
import pandas as pd

from krisk.plot.make_chart import insert_series_data


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
    else:
        raise AssertionError('This chart type is not supported in bar_line!')

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

    if kwargs['type'] == 'bar' and kwargs['trendline']:
        trendline = {'name':'trendline', 'type': 'line'}

        if c and kwargs['stacked']:
            trendline['data']  =  [0] * len(series[-1]['data'])
            trendline['stack'] = c
        elif c is None:
            trendline['data'] = series[0]['data']
        else:
            raise AssertionError('Trendline must either stacked category, or not category')

        series.append(trendline)


    
    # TODO: make annotate receive all kinds supported in echarts.


def get_bar_line_data(df, x, c, y, **kwargs):
    """Get Bar and Line manipulated data"""
    
    if c and y:
        data = df.pivot_table(
                index=x,
                values=y,
                columns=c,
                aggfunc=kwargs['how'],
                fill_value=0)
    elif c and y is None:
        data = pd.crosstab(df[x], df[c])
    elif c is None and y:
        data = df.groupby(x)[y].agg(kwargs['how'])
    else:
        data = df[x].value_counts()


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
