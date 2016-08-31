from copy import deepcopy
from krisk.plot.make_chart import insert_series_data


def set_scatter_chart(c, df, x, y, category, **kwargs):

    c.option['xAxis'] = {'type': 'value', 'name': x, 'max': int(df[x].max())}
    c.option['yAxis'] = {'type': 'value', 'name': y, 'max': int(df[y].max())}
    c.option['visualMap'] = []

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
        c.option['visualMap'].append(vmap_size)

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
    data = df[columns]
    if category:
        #Iterate and append Data for every category
        for cat, subset in data.groupby(category):
            insert_series_data(subset, x, kwargs['type'], c, cat)
    else:
        insert_series_data(data, x, kwargs['type'], c)
