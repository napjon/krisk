from krisk.chart import Chart
from copy import deepcopy


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


def insert_data_to_series(data, x, chart_type, cat=None):

    elem_series = {'name': '', 'type': chart_type, 'data': []}
    series = deepcopy(elem_series)
    series['data'] = round_list(data)
    series['type'] = chart_type
    series['name'] = cat if cat else x
    c._option['series'].append(series)


def make_chart(df, **kwargs):

    from krisk.plot.bar_line import set_bar_line_chart
    from krisk.plot.points import set_scatter_chart

    c = Chart(**kwargs)
    c._kwargs_chart_['data_columns'] = df.columns
    x = kwargs['x']
    y = kwargs.get('y')
    category = kwargs['category']

    if kwargs['type'] in ['bar', 'line', 'hist']:
        set_bar_line_chart(c, df, **kwargs)

    elif kwargs['type'] == 'scatter':
        set_scatter_chart(c, df, **kwargs)

    return c
