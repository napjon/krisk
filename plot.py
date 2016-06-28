
#from . import Chart

def bar_line_hist_condition(c,category=None,**kwargs):
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
                s['label'] = d_annotate

    if kwargs['annotate'] == 'top':
        series[-1]['label'] = d_annotate
        
        
def round_list(arr):
    try:
        return arr.values.round(3).tolist()
    except TypeError:
        return arr.unique().tolist()
    
                
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
    
    if kwargs['type'] in ['bar','line']:
        
        
        def get_bar_line_data(df):
            c._option['xAxis']['data'] = round_list(df[x].drop_duplicates())
            
            data = (df[x].value_counts()
                    if y is None else
                    df.groupby(x)[y].aggregate(kwargs['how']))
            
            return data
            
        
        insert_series_on(get_bar_line_data)
        bar_line_hist_condition(c,**kwargs)
            
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
        bar_line_hist_condition(c,**kwargs)
            
    elif kwargs['type'] == 'scatter':
        
        c._option['xAxis'] = {'type': 'value',
                              'name': x,
                              'max': int(df[x].max())}
        c._option['yAxis'] = {'type': 'value',
                              'name': y,
                              'max': int(df[y].max())}
        c._option['visualMap'] = []
        
        visual_map_template = {'show': False,
                               'min': 0,
                               'max': 999,
                               'inRange': {}}
        
        cols = [x,y]
        size = kwargs['size']
        if size is not None:
            vmap_size = deepcopy(visual_map_template)
            vmap_size['min'] = df[size].min()
            vmap_size['max'] = df[size].max()
            vmap_size['inRange']['symbolSize'] = [6,60]
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


        def get_scatter_data(df):
        
            data = df[cols]
            return data
        
        insert_series_on(get_scatter_data)
            
    return c


def bar(df,x,y=None,category=None,how='count',stacked=False,
        annotate=None,**kwargs):
    
    kwargs['x'] = x
    kwargs['y'] = y
    kwargs['category'] = category
    kwargs['how'] = how
    kwargs['type'] = 'bar'
    kwargs['stacked'] = stacked
    kwargs['annotate'] = 'top' if annotate == True else annotate
    
    return make_chart(df,**kwargs)

def line(df,x,y=None,category=None,how='count',stacked=False,area=False,
         annotate=None,**kwargs):
    
    kwargs['x'] = x
    kwargs['y'] = y
    kwargs['category'] = category
    kwargs['how'] = how
    kwargs['type'] = 'line'
    kwargs['stacked'] = stacked
    kwargs['area'] = area
    kwargs['annotate'] = 'top' if annotate == True else annotate
    
    return make_chart(df,**kwargs)

def hist(df,x,category=None,bins=10,normed=False,stacked=False,
         annotate=None,**kwargs):
    
    kwargs['x'] = x
    kwargs['category'] = category
    kwargs['bins'] = bins
    kwargs['type'] = 'hist'
    kwargs['normed'] = normed
    kwargs['stacked'] = stacked
    kwargs['annotate'] = 'top' if annotate == True else annotate
    
    return make_chart(df,**kwargs)

def scatter(df,x,y,size=None,category=None,**kwargs):
    
    kwargs['x'] = x
    kwargs['y'] = y
    kwargs['category'] = category
    kwargs['size'] = size
    #kwargs['saturate'] = saturate #TODO: Fix saturate
    kwargs['type'] = 'scatter'
    
    return make_chart(df,**kwargs)