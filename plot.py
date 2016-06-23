
def make_chart(**kwargs):
    
    c = Chart()
    
    data = kwargs['data']
    opt_data = data[kwargs['x']].value_counts().to_dict()
    
    
    if kwargs['type'] == 'bar':
        c._option_['xAxis']['data'] = list(opt_data.keys())
        c._option_['series'][0]['data'] = list(opt_data.values())
        c._option_['series'][0]['name'] = kwargs['x']
        c._option_['legend']['data'].append(kwargs['x'])
        
    
    return c
        
        
    

def Bar(data=None,x=None,y=None,category=None,how='count',**kwargs):
    
    kwargs['x'] = x
    kwargs['y'] = y
    kwargs['data'] = data
    kwargs['category'] = category
    kwargs['how'] = how
    kwargs['type'] = 'bar'
    
    return make_chart(**kwargs)
    
    