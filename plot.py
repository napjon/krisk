
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
    
    
    if kwargs['type'] in ['bar','line']:
        c._option['xAxis']['data'] = df[x].unique().tolist()
        
        def insert_series(df,cat=None,**kwargs):
            """Return data series based on dataframe"""
            
            opt_data = (df[x].value_counts()
                        if y is None else
                        df.groupby(x)[y].aggregate(kwargs['how']))

            series = deepcopy(elem_series)
            series['data'] = opt_data.values.round(3).tolist()
            series['type'] = kwargs['type']
            
            if kwargs['stacked'] == True:
                series['stack'] = category
                    
            series['name'] = cat if cat else x
            c._option['series'].append(series)
        
        
        if category:
            c._option['legend']['data'] = df[category].unique().tolist()
            
            #Iterate and append Data for every category
            for cat, subset in df.groupby(category):
                insert_series(subset,cat=cat,**kwargs)
            if (kwargs['type'] == 'line' and 
                kwargs['area'] == True and 
                kwargs['stacked']==True):
                for e in c._option['series']:
                    e['areaStyle']= {'normal': {}}

        else:
            insert_series(df,**kwargs)
            
    elif kwargs['type'] == 'hist':
        def get_hist_series(df,cat=None,bins=10,normed=False,**kwargs):
            
            y_val,x_val = np.histogram(df[x],
                                       bins=bins,
                                       normed=normed)
        
            series = deepcopy(elem_series)
            series['data'] = y_val.round(3).tolist()
            series['type'] = 'bar'
            series['name'] = cat if cat else x
                
            if kwargs['stacked'] == True:
                series['stack'] = category
            
            c._option['series'].append(series)
            
            return x_val.astype(int).tolist()
        
        if category:
            
            c._option['legend']['data'] = df[category].unique().tolist()
            for cat,subset in df.groupby(category):
                x_val = get_hist_series(subset,cat=cat,**kwargs)
                c._option['xAxis']['data'].append(x_val)
        else:
            c._option['xAxis']['data'] =  get_hist_series(df,x,**kwargs)
            
            
    return c


def bar(df,x=None,y=None,category=None,how='count',stacked=False,**kwargs):
    
    kwargs['x'] = x
    kwargs['y'] = y
    kwargs['category'] = category
    kwargs['how'] = how
    kwargs['type'] = 'bar'
    kwargs['stacked'] = stacked
    
    return make_chart(df,**kwargs)

def line(df,x=None,y=None,category=None,how='count',stacked=False,area=False,**kwargs):
    
    kwargs['x'] = x
    kwargs['y'] = y
    kwargs['category'] = category
    kwargs['how'] = how
    kwargs['type'] = 'line'
    kwargs['stacked'] = stacked
    kwargs['area'] = area
    
    return make_chart(df,**kwargs)

def hist(df,x=None,category=None,bins=10,normed=False,stacked=False,**kwargs):
    
    kwargs['x'] = x
    kwargs['category'] = category
    kwargs['bins'] = bins
    kwargs['type'] = 'hist'
    kwargs['normed'] = normed
    kwargs['stacked'] = stacked
    
    return make_chart(df,**kwargs)
    