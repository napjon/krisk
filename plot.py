
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
        if category:
            c._option_['xAxis']['data'] = df[x].unique().tolist()
            c._option_['legend']['data'] = df[category].unique().tolist()
            
            #Iterate and append Data for every category
            for cat, subset in df.groupby(category):
                opt_data = subset.ix[subset[category] == cat,x].value_counts()
                d_series = deepcopy(elem_series)
                d_series['name'] = str(cat)
                d_series['data'] = opt_data.values.tolist()
                
                if kwargs['stacked'] == True:
                    d_series['stack'] = category
                c._option_['series'].append(d_series)
        else:
            
            opt_data = df[x].value_counts()
            c._option_['xAxis']['data'] = opt_data.index.tolist()
            d_series = elem_series.copy()
            d_series['data'] = opt_data.values.tolist()
            d_series['name'] = x
            
            c._option_['series'].append(d_series)
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
    