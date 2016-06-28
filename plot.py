
#from . import Chart
def make_chart(df,**kwargs):
    
    c = Chart(**kwargs)
    
    elem_series = {
            'name': '',
            'type': kwargs['type'],
            'data': []}
    
    x = kwargs['x']
    y = kwargs.get('y')
    category = kwargs['category']
    
    def round_list(arr):
        try:
            return arr.values.round(3).tolist()
        except TypeError:
            return arr.unique().tolist()
    
    
    if kwargs['type'] in ['bar','line']:
        
        
        def insert_series(df,cat=None):
            """Return data series based on dataframe"""
            c._option['xAxis']['data'] = round_list(df[x].drop_duplicates())
            
            data = (df[x].value_counts()
                        if y is None else
                        df.groupby(x)[y].aggregate(kwargs['how']))
            
            
            series = deepcopy(elem_series)
            series['data'] = round_list(data)
            series['type'] = kwargs['type']
            
            if kwargs['stacked'] == True:
                series['stack'] = category
                    
            series['name'] = cat if cat else x
            c._option['series'].append(series)
        
        
        if category:
            #Iterate and append Data for every category
            for cat, subset in df.groupby(category):
                insert_series(subset,cat=cat)
                c._option['legend']['data'].append(cat)
        else:
            insert_series(df)
            
        if (category and
            kwargs['type'] == 'line' and 
            kwargs['area'] == True and 
            kwargs['stacked']== True):
            for e in c._option['series']:
                e['areaStyle']= {'normal': {}}
            
    elif kwargs['type'] == 'hist':
        kwargs['type'] = 'bar'
        
        
        def insert_series(df,cat=None):
            
            y_val,x_val = np.histogram(df[x],
                                       bins=kwargs['bins'],
                                       normed=kwargs['normed'])
            data = pd.Series(y_val)
            bins = x_val.astype(int).tolist()
            c._option['xAxis']['data'] = bins
            
            series = deepcopy(elem_series)
            series['data'] = round_list(data)
            series['type'] = kwargs['type']
            series['name'] = cat if cat else x
                
            if kwargs['stacked'] == True:
                series['stack'] = category
            
            c._option['series'].append(series)
            
            
        if category:
            for cat,subset in df.groupby(category):
                insert_series(subset,cat=cat)
                c._option['legend']['data'].append(cat)
        else:
            insert_series(df)
#             c._option['xAxis']['data'] =  get_hist_series(df,x,**kwargs)
            
    elif kwargs['type'] == 'scatter':
        
        c._option['xAxis'] = {'type': 'value',
                              'name': x,
                              'max': int(df[x].max())}
        
        c._option['yAxis'] = {'type': 'value',
                              'name': y,
                              'max': int(df[y].max())}
        
        
        cols = [x,y]
     
        c._option['visualMap'] = []
        visual_map_template = {'show': False,
                               'min': 0,
                               'max': 999,
                               'inRange': {}}
        
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

        def insert_series(df,cat=None):
        
            data = df[cols]
            series = deepcopy(elem_series)
            series['data'] = round_list(data)
            series['type'] = kwargs['type']
            series['name'] = cat if cat else x
            c._option['series'].append(series)
            
            
        if category:
            for cat,subset in df.groupby(category):
                insert_series(subset,cat=cat)
                c._option['legend']['data'].append(cat)
        else:
            insert_series(df)
    
            
    return c


def bar(df,x,y=None,category=None,how='count',stacked=False,**kwargs):
    
    kwargs['x'] = x
    kwargs['y'] = y
    kwargs['category'] = category
    kwargs['how'] = how
    kwargs['type'] = 'bar'
    kwargs['stacked'] = stacked
    
    return make_chart(df,**kwargs)

def line(df,x,y=None,category=None,how='count',stacked=False,area=False,**kwargs):
    
    kwargs['x'] = x
    kwargs['y'] = y
    kwargs['category'] = category
    kwargs['how'] = how
    kwargs['type'] = 'line'
    kwargs['stacked'] = stacked
    kwargs['area'] = area
    
    return make_chart(df,**kwargs)

def hist(df,x,category=None,bins=10,normed=False,stacked=False,**kwargs):
    
    kwargs['x'] = x
    kwargs['category'] = category
    kwargs['bins'] = bins
    kwargs['type'] = 'hist'
    kwargs['normed'] = normed
    kwargs['stacked'] = stacked
    
    return make_chart(df,**kwargs)

def scatter(df,x,y,size=None,category=None,**kwargs):
    
    kwargs['x'] = x
    kwargs['y'] = y
    kwargs['category'] = category
    kwargs['size'] = size
    #kwargs['saturate'] = saturate #TODO: Fix saturate
    kwargs['type'] = 'scatter'
    
    return make_chart(df,**kwargs)