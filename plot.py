
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
    
    
    if kwargs['type'] == 'bar':
        c._option_['xAxis']['data'] = df[x].unique().tolist()
        
        def return_bar_series(df,x,y=None):
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
            c._option_['legend']['data'] = df[category].unique().tolist()
            
            #Iterate and append Data for every category
            for cat, subset in df.groupby(category):
                series = return_bar_series(subset[subset[category] == cat],x,y)
                series['name'] = str(cat)
                if kwargs['stacked'] == True:
                    series['stack'] = category
                c._option_['series'].append(series)
        else:
            series = return_bar_series(df,x,y)
            
            series['name'] = x
            c._option_['series'].append(series)
            #One group doesn't need to have a legend
            #c._option_['legend']['data'].append(x)
    
    elif kwargs['type'] == 'hist':
        def get_hist_series(df,cat=None,bins=10,normed=False,**kwargs):
            
            y_val,x_val = np.histogram(df[x],
                                       bins=bins,
                                       normed=normed)
        
            series = deepcopy(elem_series)
            series['data'] = y_val.tolist()
            series['type'] = 'bar'
            if cat:
                series['name'] = str(cat)
            else:
                series['name'] = x
                
            if kwargs['stacked'] == True:
                    series['stack'] = kwargs['category']
            
            c._option_['series'].append(series)
            
            return x_val.astype(int).tolist()
        
        if category:
            
            c._option_['legend']['data'] = df[category].unique().tolist()
            xAxisData = []
            
            for cat,subset in df.groupby(category):
                xAxisData+= get_hist_series(subset[subset[category] == cat],
                                             cat=cat,**kwargs)
                
            c._option_['xAxis']['data'] = xAxisData
        else:
            c._option_['xAxis']['data'] =  get_hist_series(df,x,**kwargs)
            
            
    return c


def bar(df,x=None,y=None,category=None,how='count',stacked=False,**kwargs):
    
    kwargs['x'] = x
    kwargs['y'] = y
    kwargs['category'] = category
    kwargs['how'] = how
    kwargs['type'] = 'bar'
    kwargs['stacked'] = stacked
    
    return make_chart(df,**kwargs)

def hist(df,x=None,category=None,bins=10,normed=False,stacked=False,**kwargs):
    
    kwargs['x'] = x
    kwargs['category'] = category
    kwargs['bins'] = bins
    kwargs['type'] = 'hist'
    kwargs['normed'] = normed
    kwargs['stacked'] = stacked
    
    return make_chart(df,**kwargs)
    