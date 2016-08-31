from copy import deepcopy
import numpy as np
import pandas as pd

from krisk.plot.make_chart import insert_series_data


def set_bar_line_chart(c, df, x, category, **kwargs):

    data = None
    chart_type = kwargs['type']

    if chart_type in ['bar', 'line']:
        data = get_bar_line_data(df, x, category, **kwargs)
        c.option['xAxis']['data'] = data.index.values.tolist()

    elif chart_type == 'hist':
        chart_type = 'bar'
        data, bins = get_hist_data(df, x, category, **kwargs)
        c.option['xAxis']['data'] = bins

    if category:
        # append data for every category
        for cat in data.columns:
            insert_series_data(data[cat], x, chart_type, c, cat)
    else:
        insert_series_data(data, x, chart_type, c)

    series = c.option['series']

    ########Provide stacked,annotate, area for bar line hist#################
    d_annotate = {'normal': {'show': True, 'position': 'top'}}

    if category and kwargs['stacked']:
        for s in series:
            s['stack'] = category

            if chart_type == 'line' and kwargs['area']:
                s['areaStyle'] = {'normal': {}}

            if kwargs['annotate'] == 'all':

                if chart_type == 'bar':
                    d_ant = deepcopy(d_annotate)
                    d_ant['normal']['position'] = 'inside'
                    s['label'] = deepcopy(d_ant)
                else:
                    s['label'] = deepcopy(d_annotate)

    if kwargs['annotate'] == 'top':
        series[-1]['label'] = d_annotate
    # TODO: make annotate receive all kinds supported in echarts.


def get_bar_line_data(df, x, category, y, **kwargs):

    if category:
        if y is None:
            data = pd.crosstab(df[x], df[category])
        else:
            data = df.pivot_table(
                index=x,
                values=y,
                columns=category,
                aggfunc=kwargs['how'],
                fill_value=0)
    else:
        if y is None:
            data = df[x].value_counts()
        else:
            raise AssertionError('Use y in category instead')

    return data


def get_hist_data(df, x, category, **kwargs):

    y_val, x_val = np.histogram(
        df[x], bins=kwargs['bins'], normed=kwargs['normed'])
    bins = x_val.astype(int).tolist()

    if category:
        data = pd.DataFrame()
        for cat, sub in df.groupby(category):
            data[cat] = (pd.cut(sub[x], x_val).value_counts(
                sort=False, normalize=kwargs['normed']))
    else:
        data = pd.Series(y_val)

    return data, bins
