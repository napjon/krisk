# Krisk chart object

import uuid
import json
from copy import deepcopy
from IPython.display import Javascript
from krisk.util import get_content, join_current_dir

__all__ = ['rcParams', 'Chart']


JS_LIBS = ['echarts', 'dark', 'vintage', 'roma', 'shine', 'infographic', 'macarons']
JS_TEMPLATE_PATH = 'static/krisk.js'
EVENT_TEMPLATE_PATH = 'static/on_event.js'
HTML_TEMPLATE_PATH = 'static/template.html'
DEFAULT_CFG_PATH = 'static/defaults.json'

APPEND_ELEMENT = """
$('#{id}').attr('id','{id}'+'_old');
element.append('<div id="{id}" style="width: {width}px;height:{height}px;"></div>');"""

OPTION_TEMPLATE = {
    'title': {
        'text': ''
    },
    'tooltip': {'axisPointer': {'type': ''}},
    'legend': {
        'data': []
    },
    'xAxis': {
        'data': []
    },
    'yAxis': {},
    'series': []
}

rcParams = dict(theme='',
    size=dict(width=600,height=400),
    color=dict(background='',palette=''),
    # TODO: Add tooltip, legend, and toolbox in 0.3
    # tooltip_style=dict(trigger='item',
    #                   axis_pointer='line',
    #                   trigger_on='mousemove',
    #                   font_style='normal',
    #                   font_family='sans-serif',
    #                   font_size=14),
    # legend=dict(align='auto',
    #            orient='horizontal',
    #            x_pos='auto',
    #            y_pos='auto'),
    # toolbox=dict(save_format=None,
    #             restore=False,
    #             data_view=None,
    #             data_zoom=False,
    #             magic_type=None,
    #             brush=None,
    #             align='auto',
    #             orient='horizontal',
    #             x_pos='auto',
    #             y_pos='auto')
    )


# def set(rc):
#     DEFAULTS.update(dict)
#     return DEFAULTS


class Chart(object):
    """Chart Object"""

    def __init__(self, **kwargs):
        """Constructor"""
        # Currently, there are three type of data structure.
        # 1. Option dictionary to be passed to Echarts option
        # 2. kwargs_chart: To be passed for make_chart function
        # 3. Other than previous two


        self._chartId = str(uuid.uuid4())
        self.option = deepcopy(OPTION_TEMPLATE)
        self._kwargs_chart_ = kwargs
        self._axes_swapped = True
        self._events = {}

        self._size = rcParams['size']
        self._theme = rcParams['theme']
        self.set_color(**rcParams['color'])
        # self.set_legend(**rcParams['legend'])
        # self.set_toolbox(**rcParams['toolbox'])
        # self.set_tooltip_style(**rcParams['tooltip_style'])

    # Color and Themes

    def set_theme(self, theme):
        """
        Set the theme of the chart.
        
        Parameters
        ----------

        theme: str
            {'dark','vintage','roma','shine','infographic','macarons'}, default None
        """

        themes = JS_LIBS[1:] + ['']

        if theme not in themes:
            raise AssertionError("Invalid theme name: {theme}".format(
                theme=theme))

        self._theme = theme
        return self._get_duplicated()

    def set_color(self, background='', palette=''):
        """
        Set background and pallete color
        
        Parameters
        ----------
        background: string
            hex color
        palettes: list of strings
            list hex colors
            
        Returns
        -------
        Chart Object
        """

        #         TODO:
        #         (p
        #         .set_color(background='something')
        #         .set_color(palettes=[something])) override background to None

        #         Is this intended? Or should just these parameters made as separate methods?

        self.option.pop('color', None)
        self.option.pop('graph', None)  #Need further analyze graph color
        self.option.pop('backgroundColor', None)

        if background:
            self.option['backgroundColor'] = background
        if palette:
            self.option['color'] = palette
            self.option['graph'] = {'color': palette}

        return self._get_duplicated()

    # ---------------------------------------------------------------------------

    # Tooltip

    def set_tooltip_style(self,
                          trigger='item',
                          axis_pointer='line',
                          trigger_on='mousemove',
                          font_style='normal',
                          font_family='sans-serif',
                          font_size=14):
        """Set Tooltip options.
        
        Parameters
        ----------
        trigger: {'item',axis}, default 'item'
            When tooltip should be triggered. Default to item
        axis_pointer: {'shadow','cross','line'}, default 'line'
            Effect of pointing the axis.
        trigger_on: {'mousemove','click'}, default 'mousemove'
            Tooltip trigger
        font_style: string hex, default 'normal'
            Font Style
        font_family: sting, default to 'sans-serif'.
            Tooltip font familty
        font_size: int, default 14.
            Tooltip font size
        """

        self.option['tooltip']['trigger'] = trigger
        self.option['tooltip']['axisPointer']['type'] = axis_pointer
        self.option['tooltip']['triggerOn'] = trigger_on

        self.option['tooltip']['fontStyle'] = font_style
        self.option['tooltip']['fontFamily'] = font_family
        self.option['tooltip']['fontSize'] = font_size

        return self._get_duplicated()

    def set_tooltip_format(
            self, columns,
            formatter="'{key}' + '：' + {value} + '{unit}' +'<br>'"):
        """
        Set tooltip format. Currently only Scatter plot supported because it's the only chart that keep the
        data as is.
        
        Parameters
        ----------
        columns: list of string or list of tuples
            if list of strings, retrieve the columns value for the tooltip
            if list of tuples, will be represented as (key,unit) for the format
        override: Boolean, default to False
            provide custom Javascript function
        formatter: string,
            Format key,value,unit that will be rendered in the tooltip
        
        Returns
        -------
        Chart Object
        
        Examples
        --------
        TODO
        """

        # TODO: Make tooltip_format available to all charts.

        if self._kwargs_chart_['type'] != 'scatter':
            raise TypeError('Chart Type not supported')
        else:
            f_columns = []
            for col in columns:
                if isinstance(col, str):
                    key, unit = col, ' '
                elif isinstance(col, tuple):
                    key, unit = col
                else:
                    raise TypeError('Columns type not supported')

                idx = self._kwargs_chart_['columns'].index(key)
                f_columns.append(
                    formatter.format(
                        key=key,
                        value='value[{idx}]'.format(idx=idx),
                        unit=unit))

            formatter_strings = """function (obj) {{
                                    var value = obj.value;
                                    return {f_columns};
                                }}""".format(f_columns='+'.join(f_columns))

            self.option['tooltip']['formatter'] = formatter_strings

            return self._get_duplicated()

    # ----------------------------------------------------------------------

    def get_option(self):
        """Return Chart option that will be injected to Option Javascript object"""

        return self.option

    # ----------------------------------------------------------------------

    # Set Title, Legend and Toolbox

    def _set_object_pos(self, obj, x, y):
        """Set x,y coordinate of an object in chart layout"""

        if x.startswith('-'):
            self.option[obj]['right'] = x[1:]
        else:
            self.option[obj]['left'] = x

        if y.startswith('-'):
            self.option[obj]['top'] = y[1:]
        else:
            self.option[obj]['bottom'] = y

    def set_title(self, title, x_pos='auto', y_pos='auto'):
        """
        Set title for the plot.
        
        The coordinate is started at bottom left corner. If x_pos and y_pos started
        at negative values, then it's converted to the upper right corner (left->right, bottom->top)
        
        Parameters
        ----------
        title: str
            Title of the chart.
        x_pos: str, {'auto', left', 'center', 'right', 'i%'}, default to 'auto'
        y_pos: str, {'auto', top', 'center', 'bottom', 'i%'}, default to 'auto'
        """

        self.option['title']['text'] = title
        self._set_object_pos('title', x_pos, y_pos)

        return self._get_duplicated()

    def set_legend(self,
                   align='auto',
                   orient='horizontal',
                   x_pos='auto',
                   y_pos='auto'):
        """
        Set legend style.
        
        The coordinate is started at bottom left corner. If x_pos and y_pos started
        at negative values, then it's converted to the upper right corner (left->right, bottom->top)
        
        Parameters
        ----------
        align: str, {'auto','left','right'}, default to 'auto'
        orient: str, {'horizontal','vertical'} default to 'horizontal'
        x_pos: str, {'auto', left', 'center', 'right', 'i%'}, default to 'auto'
        y_pos: str, {'auto', top', 'center', 'bottom', 'i%'}, default to 'auto'
        
        Returns
        -------
        Chart Object
        """

        self.option['legend']['align'] = align
        self.option['legend']['orient'] = orient
        self._set_object_pos('legend', x_pos, y_pos)

        return self._get_duplicated()

    def set_toolbox(self,
                    save_format=None,
                    restore=False,
                    data_view=None,
                    data_zoom=False,
                    magic_type=None,
                    brush=None,
                    align='auto',
                    orient='horizontal',
                    x_pos='auto',
                    y_pos='auto'):
        """ Set Toolbox for the Chart
        
        The coordinate is started at bottom left corner. If x_pos and y_pos started
        at negative values, then it's converted to the upper right corner (left->right, bottom->top)
        
        Parameters
        ----------
        save_format: {None, 'png','jpeg'} default to None
        restore: Boolean, default to False
            Whether to add Restore tool to the chart
        data_view: {None, False, True}, default to None
            If not None, show the raw data, whether to treat as show only table
        data_zoom: Boolean, default to False
            Whether to add Zoom tool to the chart
        magic_type: one or more ['line', 'bar', 'stack', 'tiled'], default to None
            Add options to convert the chart to other type
        brush: one or more ['rect','polygon','lineX','lineY','keep','clear'], default to None
            Brush TOol
        align: str, {'auto','left','right'}, default to 'auto'
        orient: str, {'horizontal','vertical'} default to 'horizontal'
        x_pos: str, {'auto', left', 'center', 'right', 'i%'}, default to 'auto'
        y_pos: str, {'auto', top', 'center', 'bottom', 'i%'}, default to 'auto'
        
        Returns
        -------
        Chart Object
        
        """
        # TODO : Still exactly unclear what Brush does in option example.
        # TODO : Add Brush title english translation
        toolbox = {'feature': {}}

        d_title = {
            'dataView': 'Table View',
            'magicType': 'Chart Options',
            'restore': 'Reset',
            'saveAsImage': 'Download as Image',
            'dataZoom': 'Zoom',
            'brush': 'Brush'
        }

        def set_tool(tool, setter, val):
            if val is not None:
                d_tool = {'title': d_title[tool],
                          'show': True, }
                d_tool[setter] = val
                toolbox['feature'][tool] = d_tool

        set_tool('saveAsImage', 'type', save_format)
        set_tool('dataView', 'readOnly', data_view)
        set_tool('magicType', 'type', magic_type)
        set_tool('brush', 'type', brush)
        set_tool('restore', 'show', restore)
        set_tool('dataZoom', 'show', data_zoom)

        if data_view is not None:
            data_view_lang = ['Table View', 'Back', 'Modify']
            toolbox['feature']['dataView']['lang'] = data_view_lang

        toolbox['align'] = align
        toolbox['orient'] = orient

        self.option['toolbox'] = toolbox
        self._set_object_pos('toolbox', x_pos, y_pos)

        return self._get_duplicated()

    def set_size(self, width=600, height=400):
        """
        Set height and width of the chart in pixel
        
        Parameters
        ----------
        width: int
            Number of pixels
        height: int
            Number of pixelx
        Returns
        -------
        Chart Object
        """
        self._size['width'] = width
        self._size['height'] = height

        return self

    def flip_axes(self):
        """Flip the axes to make it horizontal"""

        self._axes_swapped = not self._axes_swapped
        self.option['xAxis'], self.option['yAxis'] = self.option[
            'yAxis'], self.option['xAxis']
        return self

    def _set_label_axes(self, xy, **kwargs):
        """Set label axes name and other customization"""
        assert xy in ['x','y']
        self.option[xy + 'Axis'].update(**kwargs)
        return self

    def set_xlabel(self, name, axis_position='middle', axis_gap=30, rotation=0, font_size=16):
        """Set x-axis label and other type of customization.

        Parameters
        ----------
        name: the label of axes
        axis_position: {start, middle, end}, default middle
            horizontal alignment of label. start will position the label at leftmost position
        axis_gap: int default 30
            vertical alignment position of label. zero start from x-axis and going further away
        rotation: int default 0
            the rotation of the label
        font_size: int default 16
            the font size of the label

        Return
        ------
        Chart object
        """
        label_kwargs = dict(name=name,
                            nameLocation=axis_position,
                            nameGap=axis_gap,
                            nameTextStyle={'fontSize':font_size},
                            nameRotate=rotation)
        return self._set_label_axes('x', **label_kwargs)

    def set_ylabel(self, name, axis_position='middle', axis_gap=30, rotation=90, font_size=16):
        """Set y-axis label and other type of customization.
        
        Parameters
        ----------
        name: the label of axes
        axis_position: {start, middle, end}, default middle
            vertical alignment of label. start will position the label at bottom position
        axis_gap: int default 30
            horizontal alignment position of label. zero start from y-axis and going further 
            away
        rotation: int default 90
            the rotation of the label
        font_size: int default 16
            the font size of the label

        Return
        ------
        Chart object
        """
        label_kwargs = dict(name=name,
                            nameLocation=axis_position,
                            nameGap=axis_gap,
                            nameTextStyle={'fontSize':font_size},
                            nameRotate=rotation)
        return self._set_label_axes('y', **label_kwargs)

    # ------------------------------------------------------------------------------------------------
    # Events
    def on_event(self, event, handler):
        """
        Calling Python handler with callback object at its arguments
        
        Parameters
        ----------
        event: {'click','dblclick','mousedown','mouseup','mouseover','mouseout','globalout'}, default None
            In which event the function should be triggered
        handler: function
            The trigger function
            
        Returns
        -------
        Chart object
        """
        events = ['click', 'dblclick', 'mousedown', 'mouseup', 'mouseover',
                  'mouseout', 'globalout']
        if event not in events:
            raise AssertionError('Invalid event name: %s' % event)

        self._events[event] = handler.__name__

        return self

    # --------------------------------------------------------------------------

    # Replot Functions

    def read_df(self, df):
        """
        Similar to resync_data, but the difference is creating new Chart object instead of replot
        on same cell
        
        Parameters
        ----------
        df: pd.DataFrame
        """
        # TODO: make data_columns only just required, except scatter.
        if (self._kwargs_chart_['data_columns'] != df.columns).all():
            raise AssertionError(
                'New data columns is not identical with existing one')
        elif df.values.shape[0] == 0:
            raise AssertionError('Empty DataFrame')

        copy_chart = deepcopy(self)

        from krisk.plot.make_chart import make_chart

        sub_chart = make_chart(df, **copy_chart._kwargs_chart_)
        copy_chart.option = sub_chart.option
        copy_chart._chartId = sub_chart._chartId
        return copy_chart

    def resync_data(self, df):
        """
        Update data in current cell but still using the same chart option.
        
        Parameters
        ----------
        df: pd.DataFrame
        """
        option = self.read_df(df).option
        return Javascript(self._get_resync_option_strings(option))

    def replot(self, chart):
        """Replot entire chart to its current cell"""
        return Javascript(self._get_resync_option_strings(chart.option))

    def _get_resync_option_strings(self, option):
        """Resync Chart option"""

        js_template = get_content(JS_TEMPLATE_PATH)
        event_template = get_content(EVENT_TEMPLATE_PATH)

        events = [event_template.format(
            event=e, function=self._events[e]) for e in self._events]

        OPTION_KWS = dict(
            requires=JS_LIBS.__repr__(),
            chartId=self._chartId,
            theme=self._theme,
            option=json.dumps(
                option, indent=4),
            events='\n'.join(events))

        return js_template.format(**OPTION_KWS)

    def _repr_javascript_(self):
        """Embedding the result of the plot to Jupyter"""
        return (APPEND_ELEMENT.format(id=self._chartId,
                                      width=self._size['width'],
                                      height=self._size['height']))+\
                (self._get_resync_option_strings(self.option))

    def _get_duplicated(self):
        chart = deepcopy(self)
        chart._chartId = str(uuid.uuid4())
        return chart
    # ----------------------------------------------------------------------

    # Saving chart option

    def to_json(self, path):
        "Save Chart option to json file"
        json.dump(self.option, open(path, 'w'), indent=4)

    def to_html(self, path):
        "Save full html file"
        # TODO: Optional add open new tab as soon as it save the html file
        from jinja2 import Template

        script = self._repr_javascript_()
        script = script.replace('element', '$("body")')

        html_template = Template(get_content(HTML_TEMPLATE_PATH))
        html_content = html_template.render(SCRIPT=script)
        with open(path, 'w') as f:
            f.write(html_content)
