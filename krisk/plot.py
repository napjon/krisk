
from krisk.make_chart import make_chart

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

def line(df,x,y=None,category=None,how=None,stacked=False,area=False,
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