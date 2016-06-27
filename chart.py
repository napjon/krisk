
import uuid

RESET_OPTION = """
require({requires},function(echarts){{
    var myChart = echarts.init(document.getElementById("{chartId}"),"{theme}");
    myChart.setOption({option});
    {events}
}});
"""
APPEND_ELEMENT = """
$('#{id}').attr('id','{id}'+'_old');
element.append('<div id="{id}" style="width: 600px;height:400px;"></div>');"""

OPTION_TEMPLATE = {
        'title': {
            'text': ''
        },
        'tooltip': {'axisPointer':{'type':''}},
        'legend': {
            'data':[]
        },
        'xAxis': {
            'data': []
        },
        'yAxis': {},
        'series': []
    }

EVENTS_TEMPLATE = """
myChart.on('{event}',function(params){{

    var d_params  = {{'series':{{'name':params.seriesName,
                                 'index':params.seriesIndex}},
                      'data':{{'value':params.value,
                               'index':params.dataIndex,
                               'name':params.name}}
    }}
    
    console.log('parameters extracted: ');
    console.log(d_params);
    
    // Create new cell and execute function passed with parameters
    var nb = Jupyter.notebook;
    nb.insert_cell_below();
    nb.select_next();
    
    var json_strings = JSON.stringify(d_params);

    var cell = nb.get_selected_cell();
    var code_input = "{function}(json.loads('" + json_strings + "'))";
    console.log("Executing code: " + code_input);
    cell.set_text(code_input);
    cell.execute();
    
    
    // Immediately delete the cell after execute
    nb.delete_cell();
    
}});
"""

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
        theme: string
            {'dark','vintage','rima','shine','infographic','dark'}, default None
        """
        
        
        if theme not in ['dark','vintage','rima','shine','infographic','dark']:
            raise AssertionError("Invalid theme name: {theme}".format(theme=theme))
            
        
        self._theme = theme
        return self
    
    def set_color(background=None,palletes=None):
        """
        Return
        """
        pass
        
        
    # ---------------------------------------------------------------------------
    
    def set_tooltip(self,trigger='axis',axis_pointer='shadow'):
        """Set Tooltip options.
        
        Parameters
        ----------
        trigger: {'axis',None}, default 'axis'
            When tooltip should be triggered. Default to axis
        axis_pointer: {'shadow',None}, default 'shadow'
            Effect of pointing the axis.
        
        
        Returns
        -------
        
        """
        
        self._option['tooltip']['trigger'] = trigger
        self._option['tooltip']['axisPointer']['type'] = axis_pointer
        return self
    
    
    def get_option(self):

        return self._option
    
    
    def set_title(self,title):
        """Set title for the plot"""
        self._option['title']['text'] = title
        return self
    
    def set_legend(self,):
        pass
    
    
    def flip_axes(self):
        """Flip the axes to make it horizontal"""
        self._axes_swapped = not self._axes_swapped
        self._option['xAxis'],self._option['yAxis'] = self._option['yAxis'],self._option['xAxis']
        return self
    
    # Events
    def on_event(self,event,handler):
        
    
        
        events = ['click','dblclick','mousedown','mouseup','mouseover','mouseout','globalout']
        if event not in events:
            raise AssertionError('Invalid event name: %s'% event)
            
        self._events[event] = handler.__name__
        return self
    
    
    
    # --------------------------------------------------------------------------
    
    # Replot Functions
    def resync_data(self,data):
        """Update data but still using the same chart option.
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
            requires=list(d_paths.keys()).__repr__(),
            chartId=self._chartId,
            theme=self._theme,
            option=json.dumps(option),
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
        pass
    
    def to_html(self,path):
        "Save full html file"
        pass
    
    
    _axes_swapped = True
    _kwargs_chart_ = {}
    _events = {}
        
    