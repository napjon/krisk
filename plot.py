
#from . import Chart
def make_chart(**kwargs):
    
    c = Chart()
    
    df = kwargs['data']
    elem_series = {
            'name': '',
            'type': kwargs['type'],
            'data': []}
    
    x = kwargs['x']
    y = kwargs['y']
    category = kwargs['category']
    
    
    if kwargs['type'] == 'bar':
        c._option_['xAxis']['data'] = df[x].unique().tolist()
        
        def return_elem_series(df,x,y=None):
            """Return data series based on dataframe"""
            grouped = df.groupby(x)
            
            if y is None:
                opt_data = grouped.aggregate('count').ix[:,-1]
            else:
                opt_data = grouped[y].aggregate(kwargs['how'])

            d_series = deepcopy(elem_series)
            d_series['data'] = opt_data.values.tolist()
            
            return d_series
        
        
        if category:
            #c._option_['xAxis']['data'] = df[x].unique().tolist()
            c._option_['legend']['data'] = df[category].unique().tolist()
            
            #Iterate and append Data for every category
            for cat, subset in df.groupby(category):
                series = return_elem_series(subset[subset[category] == cat],x,y)
                series['name'] = str(cat)
                if kwargs['stacked'] == True:
                    series['stack'] = category
                c._option_['series'].append(series)
        else:
            series = return_elem_series(df,x,y)
            
            series['name'] = x
            c._option_['series'].append(series)
            c._option_['legend']['data'].append(x)
    
    return c


def bar(df,x=None,y=None,category=None,how='count',stacked=False,**kwargs):
    
    kwargs['x'] = x
    kwargs['y'] = y
    kwargs['data'] = df
    kwargs['category'] = category
    kwargs['how'] = how
    kwargs['type'] = 'bar'
    kwargs['stacked'] = stacked
    
    return make_chart(**kwargs)
    