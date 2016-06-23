
import uuid

RESET_OPTION = """
                require(['echarts'],function(echarts){
                var myChart = echarts.init(document.getElementById('%s'));
                myChart.setOption(%s);
                });
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

class Chart():
    def __init__(self,**kwargs):
        self._chartId = str(uuid.uuid4())
        self._option_ = deepcopy(OPTION_TEMPLATE)
        
        
    def resync_data(data):
        return self
    
    
    def set_legend(self,):
        pass
    
    
    def set_theme(self,):
        pass
    
    
    def resync_data(self,option):
        return Javascript(self._get_resync_data_strings(option))
    
    
    def _get_resync_data_strings(self,option):
        return RESET_OPTION % (self._chartId,json.dumps(option))
    
    
    def set_tooltip(self,trigger='axis',axis_pointer='shadow'):
        self._option_['tooltip']['trigger'] = trigger
        self._option_['tooltip']['axisPointer']['type'] = axis_pointer
        return self
    
    
    def get_option(self):
        global optionx
        return option
    
    
    def set_title(self,s):
        self._option_['title']['text'] = s
        return self
    
    
    def flip_axes(self):
        self._axes_swapped = not self._axes_swapped
        self._option_['xAxis'],self._option_['yAxis'] = self._option_['yAxis'],self._option_['xAxis']
        return self
    
    
    def _repr_javascript_(self):
        return (APPEND_ELEMENT.format(id=self._chartId))+\
                (self._get_resync_data_strings(self._option_))
        
    _axes_swapped = True
        
        #return RESET_OPTION % (self._chartId,json.dumps(option))
    
    