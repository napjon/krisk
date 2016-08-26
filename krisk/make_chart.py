from krisk.chart import Chart
from copy import deepcopy
import numpy as np
import pandas as pd


def round_list(arr):
    try:
        return arr.values.round(3).tolist()  # Numeric Array
    except TypeError:
        try:
            return arr.unique().tolist()  #String Array
        except AttributeError:
            return (arr.apply(lambda x: x.values.round(3)  #Dataframe
                              if x.dtype.name.startswith('float') else x)
                    .values.tolist())


def make_chart(df, **kwargs):
    def insert_series_on(f, df=df):
        data = f(df)
        if category:
            #Iterate and append Data for every category
            for cat in data.columns:
                cat = str(cat)
                insert_data_to_series(data[cat], cat)
                c._option['legend']['data'].append(cat)
        else:
            insert_data_to_series(data)

    def insert_data_to_series(data, cat=None):
        series = deepcopy(elem_series)
        series['data'] = round_list(data)
        series['type'] = kwargs['type']
        series['name'] = cat if cat else x
        c._option['series'].append(series)

    c = Chart(**kwargs)
    elem_series = {'name': '', 'type': kwargs['type'], 'data': []}
    x = kwargs['x']
    y = kwargs.get('y')
    category = kwargs['category']
    c._kwargs_chart_['data_columns'] = df.columns

    def bar_line_hist_condition():
        """Provide stacked,annotate, area for bar line hist"""
        series = c._option['series']

        d_annotate = {'normal': {'show': True, 'position': 'top'}}

        if category and kwargs['stacked'] == True:
            for s in series:
                s['stack'] = category

                if kwargs['type'] == 'line' and kwargs['area'] == True:
                    s['areaStyle'] = {'normal': {}}

                if kwargs['annotate'] == 'all':

                    if kwargs['type'] == 'bar':
                        d_ant = deepcopy(d_annotate)
                        d_ant['normal']['position'] = 'inside'
                        s['label'] = deepcopy(d_ant)
                    else:
                        s['label'] = deepcopy(d_annotate)

        if kwargs['annotate'] == 'top':
            series[-1]['label'] = d_annotate
        # TODO: make annotate receive all kinds supported in echarts.

    if kwargs['type'] in ['bar', 'line']:

        @insert_series_on
        def get_bar_line_data(df):

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

            c._option['xAxis']['data'] = data.index.values.tolist()

            return data

        bar_line_hist_condition()

    elif kwargs['type'] == 'hist':
        kwargs['type'] = 'bar'

        @insert_series_on
        def get_hist_data(df):

            y_val, x_val = np.histogram(
                df[x], bins=kwargs['bins'], normed=kwargs['normed'])
            if category:
                data = pd.DataFrame()
                for cat, sub in df.groupby(category):
                    data[cat] = (pd.cut(sub[x], x_val).value_counts(
                        sort=False, normalize=kwargs['normed']))
            else:
                data = pd.Series(y_val)

            bins = x_val.astype(int).tolist()
            c._option['xAxis']['data'] = bins

            return data

        bar_line_hist_condition()

    elif kwargs['type'] == 'scatter':

        c._option['xAxis'] = {'type': 'value',
                              'name': x,
                              'max': int(df[x].max())}
        c._option['yAxis'] = {'type': 'value',
                              'name': y,
                              'max': int(df[y].max())}
        c._option['visualMap'] = []

        cols = [x, y]
        size = kwargs['size']
        if size is not None:
            vmap_template_size = {'show': False,
                                  'dimension': 2,
                                  'min': 0,
                                  'max': 250,
                                  'precision': 0.1,
                                  'inRange': {'symbolSize': [10, 70]}}
            vmap_size = deepcopy(vmap_template_size)
            vmap_size['min'] = df[size].min()
            vmap_size['max'] = df[size].max()
            vmap_size['inRange']['symbolSize'] = list(kwargs['size_px'][:2])
            c._option['visualMap'].append(vmap_size)
            cols.append(size)

        #TODO: Fix Saturate
        #          saturate = kwargs['saturate']
        #         if saturate is not None:
        #             vmap_saturate = deepcopy(visual_map_template)
        #             vmap_saturate['min'] = float(df[saturate].min())
        #             vmap_saturate['max'] = float(df[saturate].max())
        #             vmap_saturate['inRange']['colorLightness'] = [1,0.5]
        #             c._option['visualMap'].append(vmap_saturate)
        #             cols.append(saturate)

        columns = cols + df.columns.difference(cols).tolist()
        c._kwargs_chart_['columns'] = columns

        def insert_scatter_data(df):
            data = df[columns]
            if category:
                #Iterate and append Data for every category
                for cat, subset in data.groupby(category):
                    cat = str(cat)
                    insert_data_to_series(subset, cat)
                    c._option['legend']['data'].append(cat)
            else:
                insert_data_to_series(data)

        insert_scatter_data(df)

    return c
