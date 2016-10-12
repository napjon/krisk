from krisk.plot.make_chart import make_chart


def bar(df,
        x,
        y=None,
        c=None,
        how='count',
        stacked=False,
        annotate=None,
        full=False,
        trendline=False,
        sort_on='index',
        sort_c_on=None,
        ascending=True):
    """
    Parameters
    ----------
    df: pd.DataFrame
        data to be used for the chart
    x: string
        columns to be used as category axis
    y: string, default None
        if None, use count of category value. otherwise aggregate based on y columns
    category: string, default None
        another grouping columns inside x-axis
    how: string, default None
        to be passed to pd.group_by(x).aggregate(how). Can be mean,median, or any 
        reduced operations.
    stacked: Boolean, default False.
        Whether to stacked category on top of the other categories.
    annotate: string, {'all',True} default None
        if True, annotate value on top of the plot element. If stacked is also True, annotate the 
        last category. if 'all' and stacked, annotate all category
    full: boolean, default False.
        If true, set to full area stacked chart. Only work if stacked is True.
    trendline: boolean, default False.
        If true, add line that connected the bars. Only work if not category, category but stacked,
        or not full.
    sort_on: {'index', 'values', int, 'count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'},
         default 'index'.
        Add sort mode. Only work when c is None.
        If index, sort index on lexicographical order. use as s.sort_index()
        if values, sort based on values. Use as s.sort_values()
        If string, deviation from value provided by pd.Series.describe()
        if integer, treat as value and deviate from that value
    sort_c_on: string, default None.
        specify a category as basis sort value if c is specified. Must be specified when use 
        sort_on other than default value.
    ascending: boolean, default True
        sort ascending vs. descending
    
    Returns
    -------
    Chart Object
    """
    return make_chart(df,type='bar',x=x,y=y,c=c,how=how,stacked=stacked,full=full,
                      trendline=trendline, sort_on=sort_on, sort_c_on=sort_c_on, ascending=ascending,
                      annotate='top' if annotate == True else annotate)


def line(df,
         x,
         y=None,
         c=None,
         how=None,
         stacked=False,
         area=False,
         annotate=None,
         full=False,
         smooth=False,
         sort_on='index',
         sort_c_on=None,
         ascending=True):
    """
    Parameters
    ----------
    df: pd.DataFrame
        data to be used for the chart
    x: string
        columns to be used as category axis
    y: string, default None
        if None, use count of category value. otherwise aggregate based on y columns
    c: string, default None
        category column inside x-axis
    how: string, default None
        to be passed to pd.group_by(x).aggregate(how). Can be mean,median, or any 
        reduced operations.
    stacked: Boolean, default False.
        Whether to stacked category on top of the other categories.
    annotate: string, {'all',True} default None
        if True, annotate value on top of the plot element. If stacked is also True, annotate the last
        category. if 'all' and stacked, annotate all category
    full: boolean, default False.
        If true, set to full area stacked chart. Only work if stacked is True.
    smooth: boolean, default False.
        If true, smooth the line.
   sort_on: {'index', 'values', int, 'count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'},
         default 'index'.
        Add sort mode. Only work when c is None.
        If index, sort index on lexicographical order. use as s.sort_index()
        if values, sort based on values. Use as s.sort_values()
        If string, deviation from value provided by pd.Series.describe()
        if integer, treat as value and deviate from that value
    sort_c_on: string, default None.
        specify a category as basis sort value if c is specified. Must be specified when use 
        sort_on other than default value.
    ascending: boolean, default True
        sort ascending vs. descending
        
    Returns
    -------
    Chart Object
    """
    return make_chart(df,type='line',x=x,y=y,c=c,how=how,stacked=stacked,area=area,full=full,
                      smooth=smooth, sort_on=sort_on, sort_c_on=sort_c_on, ascending=ascending,
                      annotate='top' if annotate == True else annotate)


def hist(df,
         x,
         c=None,
         bins=10,
         normed=False,
         stacked=False,
         annotate=None,
         density=False):
    """
    Parameters
    ----------
    df: pd.DataFrame
        data to be used for the chart
    x: string
        columns to be used as category axis
    c: string, default None
        another grouping columns inside x-axis
    bins: int, default 10
        Set number of bins in histogram
    normed: boolean, default False
        Whether normalize the histogram
    stacked: Boolean, default False.
        Whether to stacked category on top of the other categories.
    annotate: string, {'all',True} default None
        if True, annotate value on top of the plot element. If stacked is also True, annotate the last
        category. if 'all' and stacked, annotate all category
    density: boolean, default False.
        Whether to add density to the plot
    
    Returns
    -------
    Chart Object
    """
    return make_chart(df,type='hist',x=x,c=c,bins=bins,normed=normed,stacked=stacked,
                      density=density,
                      annotate='top' if annotate == True else annotate)
   

def scatter(df, x, y, s=None, c=None, saturate=None, size_px=(10, 70)):
    """
    Parameters
    ----------
    df: pd.DataFrame
        data to be used for the chart
    x,y: string, columns in pd.DataFrame
        Used as coordinate in scatter chart
    s: string, columns in pd.DataFrame default None
        Used as sizing value of the scatter points
    c: string, default None
        column used as grouping color category
    saturation
    size_px: tuple, default (10,70)
        boundary size, lower and upper limit in pixel for min-max scatter points

        
    Returns
    -------
    Chart Object
    """
    return make_chart(df,type='scatter',x=x,y=y,s=s,c=c,saturate=saturate,size_px=size_px)
