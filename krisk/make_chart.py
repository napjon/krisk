
from krisk.chart import Chart
from copy import deepcopy

def round_list(arr):
    try:
        return arr.values.round(3).tolist() # Numeric Array
    except TypeError:
        try:
            return arr.unique().tolist() #String Array
        except AttributeError:
            return (arr.apply(lambda x: x.values.round(3) #Dataframe
                            if x.dtype.name.startswith('float') 
                            else x)
                    .values.tolist())
    
                
def make_chart(df,**kwargs):
    
    def insert_series_on(f):

        if category:
            #Iterate and append Data for every category
            for cat, subset in df.groupby(category):
                cat = str(cat)
                insert_data_to_series(f,subset,cat)
                c._option['legend']['data'].append(cat)
        else:
            insert_data_to_series(f,df)
    
    
    def insert_data_to_series(f,df,cat=None):
        data = f(df)
        series = deepcopy(elem_series)
        series['data'] = round_list(data)
        series['type'] = kwargs['type']
        series['name'] = cat if cat else x
        c._option['series'].append(series)
        
    
    c = Chart(**kwargs)
    
    elem_series = {
            'name': '',
            'type': kwargs['type'],
            'data': []}
    
    x = kwargs['x']
    y = kwargs.get('y')
    category = kwargs['category']
    
    
    def bar_line_hist_condition():
        """Provide stacked,annotate, area for bar line hist"""
        series = c._option['series']

        d_annotate = {'normal':{'show':True,
                                'position':'top'}}

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
    
    
    if kwargs['type'] in ['bar','line']:
       
        
        
        def get_bar_line_data(df):
            c._option['xAxis']['data'] = round_list(df[x].drop_duplicates())
#             c._option['yAxis']['scale'] = True
            
            if y is None:
                data = df[x].value_counts()
            else:
                data = (df[y]
                        if kwargs['how'] is None else
                        df.groupby(x)[y].aggregate(kwargs['how']))
                    
                
#             data = (df[x].value_counts()
#                     if y is None else
#                     df.groupby(x)[y].aggregate(kwargs['how']))
            
            return data
            
        
        insert_series_on(get_bar_line_data)
        bar_line_hist_condition()
            
    elif kwargs['type'] == 'hist':
        kwargs['type'] = 'bar'
        
        
        def get_hist_data(df):
            
            y_val,x_val = np.histogram(df[x],
                                       bins=kwargs['bins'],
                                       normed=kwargs['normed'])
            data = pd.Series(y_val)
            bins = x_val.astype(int).tolist()
            c._option['xAxis']['data'] = bins
            
            return data
        
        insert_series_on(get_hist_data)
        bar_line_hist_condition()
            
    elif kwargs['type'] == 'scatter':
        
        c._option['xAxis'] = {'type': 'value',
                              'name': x,
                              'max': int(df[x].max())}
        c._option['yAxis'] = {'type': 'value',
                              'name': y,
                              'max': int(df[y].max())}
        c._option['visualMap'] = []
        
        
        
        cols = [x,y]
        size = kwargs['size']
        if size is not None:
            vmap_template_size = {
                                    'show': False,
                                    'dimension': 2,
                                    'min': 0,
                                    'max': 250,
                                    'precision': 0.1,
                                    'inRange': {
                                        'symbolSize': [10, 70]
                                    }
                                }
            vmap_size = deepcopy(vmap_template_size)
            vmap_size['min'] = df[size].min()
            vmap_size['max'] = df[size].max()
#             vmap_size['inRange']['symbolSize'] = [30,100]
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

        columns = cols+df.columns.difference(cols).tolist()
        c._kwargs_chart_['columns'] = columns
        
        def get_scatter_data(df):
            data = df[columns]
#             print(columns)
            return data
        
        insert_series_on(get_scatter_data)
    
        
            
    return c