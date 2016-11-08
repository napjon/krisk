from copy import deepcopy
from krisk.plot.make_chart import insert_series_data


def set_scatter_chart(chart, df, x, y, c, **kwargs):

    chart.option['xAxis'] = {'type': 'value', 'name': x, 'max': int(df[x].max())}
    chart.option['yAxis'] = {'type': 'value', 'name': y, 'max': int(df[y].max())}
    chart.option['visualMap'] = []

    cols = [x, y]
    s = kwargs['s']
    dimension = 1
    if s is not None:
        dimension += 1
        cols.append(s)

        vmap_size = dict(show=False,
                         dimension=dimension,
                         precision=0.1,
                         min=df[s].min(),
                         max=df[s].max(),
                         inRange={'symbolSize': list(kwargs['size_px'][:2])})
        chart.option['visualMap'].append(vmap_size)

    #TODO: Fix Saturate for large value
    saturate = kwargs['saturate']
    if saturate is not None:
        dimension += 1
        cols.append(saturate)

        vmap_saturate = dict(show=False,
                             dimension=dimension,
                             min=df[saturate].min(),
                             max=df[saturate].max(),
                             inRange={'colorLightness': [0.1, 0.9]})
        chart.option['visualMap'].append(vmap_saturate)
        
    columns = cols + df.columns.difference(cols).tolist()
    chart._kwargs_chart_['columns'] = columns
    data = df[columns]
    if c:
        #Iterate and append Data for every category
        for cat, subset in data.groupby(c):
            insert_series_data(subset, x, kwargs['type'], chart, cat)
    else:
        insert_series_data(data, x, kwargs['type'], chart)
