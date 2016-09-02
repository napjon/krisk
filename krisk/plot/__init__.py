from krisk.plot.make_chart import make_chart


def bar(df,
        x,
        y=None,
        c=None,
        how='count',
        stacked=False,
        annotate=None,
        full=False):
    """
    Parameters
    ----------
    df: pd.DataFrame
        data to be used for the chart
    x: string
        columns to be used as category axis
    y: string, default to None
        if None, use count of category value. otherwise aggregate based on y columns
    category: string, default to None
        another grouping columns inside x-axis
    how: string, default to None
        to be passed to pd.group_by(x).aggregate(how). Can be mean,median, or any 
        reduced operations.
    stacked: Boolean, default to False.
        Whether to stacked category on top of the other categories.
    annotate: string, {'all',True} default to None
        if True, annotate value on top of the plot element. If stacked is also True, annotate the last
        category. if 'all' and stacked, annotate all category
    full: boolean, default to False.
        If true, set to full area stacked chart. Only work if stacked is True.
    
    Returns
    -------
    Chart Object
    """

    # TODO: add optional argument trendline

    return make_chart(df,type='bar',x=x,y=y,c=c,how=how,stacked=stacked,full=full,
                      annotate='top' if annotate == True else annotate)


def line(df,
         x,
         y=None,
         c=None,
         how=None,
         stacked=False,
         area=False,
         annotate=None,
         full=False):
    """
    Parameters
    ----------
    df: pd.DataFrame
        data to be used for the chart
    x: string
        columns to be used as category axis
    y: string, default to None
        if None, use count of category value. otherwise aggregate based on y columns
    c: string, default to None
        category column inside x-axis
    how: string, default to None
        to be passed to pd.group_by(x).aggregate(how). Can be mean,median, or any 
        reduced operations.
    stacked: Boolean, default to False.
        Whether to stacked category on top of the other categories.
    annotate: string, {'all',True} default to None
        if True, annotate value on top of the plot element. If stacked is also True, annotate the last
        category. if 'all' and stacked, annotate all category
    full: boolean, default to False.
        If true, set to full area stacked chart. Only work if stacked is True.
    
    Returns
    -------
    Chart Object
    """
    return make_chart(df,type='line',x=x,y=y,c=c,how=how,stacked=stacked,area=area,full=full,
                      annotate='top' if annotate == True else annotate)


def hist(df,
         x,
         c=None,
         bins=10,
         normed=False,
         stacked=False,
         annotate=None):
    """
    Parameters
    ----------
    df: pd.DataFrame
        data to be used for the chart
    x: string
        columns to be used as category axis
    c: string, default to None
        another grouping columns inside x-axis
    bins: int, default to 10
        Set number of bins in histogram
    normed: boolean, default to False
        Whether normalize the histogram
    stacked: Boolean, default to False.
        Whether to stacked category on top of the other categories.
    annotate: string, {'all',True} default to None
        if True, annotate value on top of the plot element. If stacked is also True, annotate the last
        category. if 'all' and stacked, annotate all category 
    
    Returns
    -------
    Chart Object
    """
    return make_chart(df,type='hist',x=x,c=c,bins=bins,normed=normed,stacked=stacked,
                      annotate='top' if annotate == True else annotate)
   

def scatter(df, x, y, s=None, c=None, size_px=(10, 70)):
    """
    Parameters
    ----------
    df: pd.DataFrame
        data to be used for the chart
    x,y: string, columns in pd.DataFrame
        Used as coordinate in scatter chart
    s: string, columns in pd.DataFrame default to None
        Used as sizing value of the scatter points
    c: string, default to None
        column used as grouping color category
    size_px: tuple, default to (10,70)
        boundary size, lower and upper limit in pixel for min-max scatter points
        
    Returns
    -------
    Chart Object
    """
    #TODO add saturation
    return make_chart(df,type='scatter',x=x,y=y,s=s,c=c,size_px=size_px)
