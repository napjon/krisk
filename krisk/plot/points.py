from copy import deepcopy
from krisk.plot.make_chart import insert_series_data


def set_scatter_chart(chart, df, x, y, c, **kwargs):

    chart.option['xAxis'] = {'type': 'value', 'name': x, 'max': int(df[x].max())}
    chart.option['yAxis'] = {'type': 'value', 'name': y, 'max': int(df[y].max())}
    chart.option['visualMap'] = []

    cols = [x, y]
    size = kwargs['size']
    if size is not None:
        cols.append(size)

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
        chart.option['visualMap'].append(vmap_size)

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
    chart._kwargs_chart_['columns'] = columns
    data = df[columns]
    if c:
        #Iterate and append Data for every category
        for cat, subset in data.groupby(c):
            insert_series_data(subset, x, kwargs['type'], chart, cat)
    else:
        insert_series_data(data, x, kwargs['type'], chart)
