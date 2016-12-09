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
        if None, use count of category. otherwise aggregate based on y columns
    c: string, default None
        another grouping columns inside x-axis
    how: string, default None
        to be passed to pd.group_by(x).aggregate(how). Can be mean,median,
        or any reduced operations.
    stacked: Boolean, default False.
        Whether to stacked category on top of the other categories.
    annotate: string, {'all', True, None} default None
        if True, annotate value on top of the plot element. If stacked is
        also True, annotate the last category. if 'all' and stacked,
        annotate all category
    full: boolean, default False.
        If true, set to full area stacked chart. Only work if stacked is True.
    trendline: boolean, default False.
        If true, add line that connected the bars. Only work if not category,
        category but stacked, or not full.
    sort_on: {'index', 'values', int, function}, default 'index'.
        If index, sort index on lexicographical order. use as s.sort_index()
        if values, sort based on values. Use as s.sort_values()
        If function, use it as aggregate (e.g. grouped.agg('mean' or np.mean))
        if integer, treat as value and deviate from that value
    sort_c_on: string, default None.
        specify a category as basis sort value if c is specified. Must be
        specified when use sort_on other than default value.
    ascending: boolean, default True
        sort ascending vs. descending
    
    Returns
    -------
    Chart Object
    """

    return make_chart(df,type='bar',x=x,y=y,c=c,how=how,stacked=stacked,
                      full=full, trendline=trendline,
                      sort_on=sort_on, sort_c_on=sort_c_on, ascending=ascending,
                      annotate='top' if annotate is True else annotate)


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
        if None, use count of category. otherwise aggregate based on y columns
    c: string, default None
        category column inside x-axis
    how: string, default None
        to be passed to pd.group_by(x).aggregate(how). Can be mean,median,
        or any reduced operations.
    stacked: boolean, default False.
        Whether to stacked category on top of the other categories.
    area: boolean, default False.
        Whether to fill the area with line colors.
    annotate: string, {'all',True} default None
        if True, annotate value on top of the plot element. If stacked is
        also True, annotate the last category. if 'all' and stacked,
        annotate all category
    full: boolean, default False.
        If true, set to full area stacked chart. Only work if stacked is True.
    smooth: boolean, default False.
        If true, smooth the line.
    sort_on: {'index', 'values', int, function}, default 'index'.
        If index, sort index on lexicographical order. use as s.sort_index()
        if values, sort based on values. Use as s.sort_values()
        If function, use it as aggregate (e.g. grouped.agg('mean' or np.mean))
        if integer, treat as value and deviate from that value
    sort_c_on: string, default None.
        specify a category as basis sort value if c is specified. Must be
        specified when use sort_on other than default value.
    ascending: boolean, default True
        sort ascending vs. descending
        
    Returns
    -------
    Chart Object
    """
    return make_chart(df,type='line',x=x,y=y,c=c,how=how,stacked=stacked,
                      area=area,full=full, smooth=smooth,
                      sort_on=sort_on, sort_c_on=sort_c_on, ascending=ascending,
                      annotate='top' if annotate is True else annotate)


def line_tidy(df,
              full=False,
              stacked=False,
              area=False,
              annotate=False,
              smooth=False):

    """
    This plot assume DataFrame can be directly consumed (tidy data). Used for
    customized manipulation data that normal plot can't provides.
        * data is only 2-dimension. There is no hierarchical columns or index.
        * data is cleaned and aggregated.
        * No duplicate values for each index-column pair (tidy)
        * index is used for category x-axis.
        * each column corresponds to one series.
        * values in one column belong to column data series.
    df: pd.DataFrame
        data to be used for the chart
    stacked: boolean, default False.
        Whether to stacked category on top of the other categories.
    area: boolean, default False.
        Whether to fill the area with line colors.
    full: boolean, default False.
        If true, set to full area stacked chart. Only work if stacked is True.
    annotate: string, {'all', True, None} default None
        if True, annotate value on top of the plot element. If stacked is
        also True, annotate the last category. if 'all' and stacked,
        annotate all category
    smooth: boolean, default False.
        If true, smooth the line.

    Returns
    -------
    Chart Object
    """
    return make_chart(df, x=df.index.name, c="unnamed",
                      stacked=stacked, area=area, full=full,
                      type='line_tidy', smooth=smooth,
                      annotate='top' if annotate is True else annotate)


def bar_tidy(df,
             full=False,
             stacked=False,
             trendline=False,
             annotate=None):

    """
    This plot assume DataFrame can be directly consumed (tidy data). Used for
    customized manipulation data that normal plot can't provides.
        * data is only 2-dimension. There is no hierarchical columns or index.
        * data is cleaned and aggregated.
        * no duplicate values for each index-column pair (tidy)
        * index is used for category x-axis.
        * each column corresponds to one series.
        * values in one column belong to column data series.
    df: pd.DataFrame
        data to be used for the chart
    stacked: boolean, default False.
        Whether to stacked category on top of the other categories.
    full: boolean, default False.
        If true, set to full area stacked chart. Only work if stacked is True.
    trendline: boolean, default False.
        If true, add line that connected the bars. Only work if not category,
        category but stacked, or not full.
    annotate: string, {'all', True, None} default None
        if True, annotate value on top of the plot element. If stacked is
        also True, annotate the last category. if 'all' and stacked,
        annotate all category
    Returns
    -------
    Chart Object
    """
    return make_chart(df, x=df.index.name, c="unnamed",
                      stacked=stacked, full=full,
                      type='bar_tidy', trendline=trendline,
                      annotate='top' if annotate is True else annotate)


def bar_line(df, x, ybar, yline, bar_aggfunc='mean', line_aggfunc='mean',
             sort_on='index', ascending=True, is_distinct=False,
             hide_split_line=True, style_tooltip=True):
    """
    Parameters
    ----------
    df: pd.DataFrame
        data to be used for the chart
    x: string
        column to be used as category axis
    ybar: string
        column to be used as bar values
    yline:
        column to be used as line values
    bar_aggfunc: string (mapping function) or function, default 'mean'
        Function to use for aggregating groups on bar values
    line_aggfunc: string (mapping function) or function, default 'mean'
        Function to use for aggregating groups on line values
    sort_on: {'index', 'ybar', 'yline'}, default 'index'
        sorting x-axis. If index, sort on x. if either `ybar` or `yline`,
        sort based on values
    ascending: boolean, default True
        sort ascending vs. descending
    is_distinct: boolean, default False
        Don't use aggregation on this data. Will use drop_duplicates instead.
        Ignore `bar_aggfunc`, `line_aggfunc`, `sort_on`, `ascending` parameters.
        sort_on deliberately disabled in is_distinct mode to allow already
        sorted distinct data.
    hide_split_line: boolean, default True
        Whether to hide the split line of both y-axis.
    style_tooltip: boolean, default True
        Whether to offer help to style tooltip. If True, execute
        `chart.set_tooltip_style(trigger='axis',axis_pointer='shadow')`

    Returns
    -------
    Chart Object
    """
    if sort_on not in ['index', 'ybar', 'yline']:
        raise ValueError("Invalid Parameters")

    return make_chart(df, x=x, ybar=ybar, yline=yline,
                      bar_aggfunc=bar_aggfunc, line_aggfunc=line_aggfunc,
                      is_distinct=is_distinct,
                      sort_on=sort_on, ascending=ascending,
                      hide_split_line=hide_split_line,
                      style_tooltip=style_tooltip,
                      c=None, type='bar_line')


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
    annotate: string, {'all',True, None} default None
        if True, annotate value on top of the plot element. If stacked is also
        True, annotate the last category. if 'all' and stacked, annotate all
        category
    density: boolean, default False.
        Whether to add density to the plot
    
    Returns
    -------
    Chart Object
    """
    return make_chart(df,type='hist',x=x,c=c,bins=bins,normed=normed,
                      stacked=stacked, density=density,
                      annotate='top' if annotate is True else annotate)
   

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
    saturate: string, default None
        column to use for saturation
    size_px: tuple, default (10,70)
        boundary size, lower and upper limit in pixel for min-max scatter points

    Returns
    -------
    Chart Object
    """
    return make_chart(df,type='scatter',x=x,y=y,s=s,c=c,
                      saturate=saturate,size_px=size_px)


def waterfall(s, color_coded=False, annotate=None,
              up_name='positive', down_name='negative'):
    """
    Firxt category axis automatically not float.

    Parameters
    ----------
    s: pd.Series
    color_coded: boolean, default to False
        Whether to color coded negative and positive values
    annotate: {'inside', 'outside', None}, default to None
        annotate the bar with actual value.
    up_name,down_name: string
        increase/decrease bar name. Only work if color_coded is True

    Returns
    -------
    Chart Object
    """
    if annotate not in [None, 'inside', 'outside']:
        raise ValueError("invalid parameters")

    return make_chart(s, type='waterfall', up_name=up_name, down_name=down_name,
                      color_coded=color_coded, annotate=annotate)


