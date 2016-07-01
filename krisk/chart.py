
import uuid
import json
from copy import deepcopy
from krisk.template import *
from krisk.connections import get_paths

paths = list(get_paths())




class Chart():
    def __init__(self,**kwargs):
        self._chartId = str(uuid.uuid4())
        self._option = deepcopy(OPTION_TEMPLATE)    
        self._kwargs_chart_ = kwargs
        self._theme = ''
        
        
    # Color and Themes
    
    def set_theme(self,theme):
        """
        Set the theme of the chart.
        
        Parameters
        ----------

        theme: str
            {'dark','vintage','roma','shine','infographic','macarons'}, default None
        """
        
        
        if theme not in THEMES:
            raise AssertionError("Invalid theme name: {theme}".format(theme=theme))
            
        
        self._theme = theme
        return self
    
    
    def set_color(self,background='',palette=''):
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
        
        self._option.pop('color',None)
        self._option.pop('graph',None) #Need further analyze graph color
        self._option.pop('backgroundColor',None)
        
        if background:
            self._option['backgroundColor'] = background
        if palettes:
            self._option['color'] = palettes
            self._option['graph'] = {'color':palettes}
        
        
        return self
        
        
        
    # ---------------------------------------------------------------------------
    
    # Tooltip
    
    def set_tooltip_style(self,trigger='item',axis_pointer='line',trigger_on='mousemove',
                          font_style='normal',font_family='sans-serif',font_size=14):
        
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
        
        
        self._option['tooltip']['trigger'] = trigger
        self._option['tooltip']['axisPointer']['type'] = axis_pointer
        self._option['tooltip']['triggerOn'] = trigger_on
        
        self._option['tooltip']['fontStyle'] = font_style
        self._option['tooltip']['fontFamily'] = font_family
        self._option['tooltip']['fontSize'] = font_size
        
        return self
    
    
    def set_tooltip_format(self,columns,override=False,
                           formatter = "'{key}' + '：' + {value} + '{unit}' +'<br>'"):
        """
        Set tooltip format. Currently only Scatter plot supported because it's the only that keep the
        data as is.
        
        Parameters
        ----------
        
        columns: list of string or list of tuples
            if list of strings, retrieve the columns value for the tooltip
            if list of tuples, will be represented as key,unit for the format
        override: Boolean, default to False
            provide custom Javascript function
        formatter: string,
            Format key,value,unit that will be rendered in the tooltip
        
        Returns
        -------
        Chart Object
        
        Examples
        --------
        
        """
        
        if self._kwargs_chart_['type'] != 'scatter':
            raise TypeError('Chart Type not supported')
        else:
            f_columns = []
            for c in columns:
                if isinstance(c,str):
                    key,unit =c, ' '
                elif isinstance(c,tuple):
                    key,unit = c
                else:
                    raise TypeError('Columns type not supported')

                idx = self._kwargs_chart_['columns'].index(key)
                f_columns.append(formatter
                                 .format(key=key,
                                         value='value[{idx}]'.format(idx=idx),
                                         unit=unit))

            formatter_strings =  """function (obj) {{
                                    var value = obj.value;
                                    return {f_columns};
                                }}""".format(f_columns='+'.join(f_columns))

            self._option['tooltip']['formatter'] = formatter_strings
            

            return self
    
    # ----------------------------------------------------------------------
    
    def get_option(self):
        """Return Chart option that will be injected to Option Javascript object"""

        return self._option
    
    
    def set_title(self,title,x_pos='auto',y_pos='auto'):
        """Set title for the plot.
        
        The coordinate is started at bottom left corner. If x_pos and y_pos started
        at negative values, then the coordinate started at upper right corner.
        
        Parameters
        ----------
        title: str
            Title of the chart.
        x_pos: str, {'auto', left', 'center', 'right', 'i%'}, default to 'auto'
        y_pos: str, {'auto', top', 'center', 'bottom', 'i%'}, default to 'auto'
        
        """
        
        self._option['title']['text'] = title
        
        if x_pos.startswith('-'):
            self._option['title']['right'] = x_pos[1:]
        else:
            self._option['title']['left'] = x_pos
            
        if y_pos.startswith('-'):
            self._option['title']['top'] = y_pos[1:]
        else:
            self._option['title']['bottom'] = y_pos
        
        
        return self
    
    
    def set_legend(self,align='auto',orient='horizontal',
                   x_pos='auto',y_pos='auto'):
        """
        Set legend style.
        
        The coordinate is started at bottom left corner. If x_pos and y_pos started
        at negative values, then the coordinate started at upper right corner.
        
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
        
        self._option['legend']['align'] = align
        self._option['legend']['orient'] = orient
        
        if x_pos.startswith('-'):
            self._option['legend']['right'] = x_pos[1:]
        else:
            self._option['legend']['left'] = x_pos
            
        if y_pos.startswith('-'):
            self._option['legend']['top'] = y_pos[1:]
        else:
            self._option['legend']['bottom'] = y_pos
            
            
        return self
    
    
    def flip_axes(self):
        """Flip the axes to make it horizontal"""
        
        self._axes_swapped = not self._axes_swapped
        self._option['xAxis'],self._option['yAxis'] = self._option['yAxis'],self._option['xAxis']
        return self
    
    # Events
    def on_event(self,event,handler):
        """
        Parameter:
        event: {'click','dblclick','mousedown','mouseup','mouseover','mouseout','globalout'}, default None
            In which event the function should be triggered
        handler: function
            The trigger function
        """
        
        events = ['click','dblclick','mousedown','mouseup','mouseover','mouseout','globalout']
        if event not in events:
            raise AssertionError('Invalid event name: %s'% event)
            
        self._events[event] = handler.__name__
        return self
    
    
    
    # --------------------------------------------------------------------------
    
    # Replot Functions
    def resync_data(self,data):
        """
        Update data but still using the same chart option.
        Currently just update the current cell it exist, but not the chart option
        itself.
        
        Parameters
        ----------
        data: pd.DataFrame
         
        """
        option = make_chart(data,**self._kwargs_chart_)._option
        return Javascript(self._get_resync_option_strings(option))
    
    def replot(self,chart):
        """Replot entire chart to its current cell"""
        return Javascript(self._get_resync_option_strings(chart._option))
    
    def _get_resync_option_strings(self,option):
        """Resync Chart option"""
        
        events = [EVENTS_TEMPLATE.format(event=e,function=self._events[e]) for e in self._events]
        OPTION_KWS = dict(
            requires=paths.__repr__(),
            chartId=self._chartId,
            theme=self._theme,
            option=json.dumps(option,indent=4),
            events='\n'.join(events)
        )
        return RESET_OPTION.format(**OPTION_KWS)
    
    
    def _repr_javascript_(self):
        """Embedding the result of the plot to Jupyter"""
        return (APPEND_ELEMENT.format(id=self._chartId))+\
                (self._get_resync_option_strings(self._option))
    # ----------------------------------------------------------------------
    
    # Saving chart option
    def to_json(self,path):
        "Save Chart option"
        
        json.dump(self._option,open(path,'w'))
        
    
    def to_html(self,path):
        "Save full html file"
        save_html(self._repr_javascript_(),path)
    
    
    _axes_swapped = True
    _kwargs_chart_ = {}
    _events = {}
        
    