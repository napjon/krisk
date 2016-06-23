
RESET_OPTION = """
                require(['echarts'],function(echarts){
                var myChart = echarts.init(document.getElementById('%s'));
                myChart.setOption(%s);
                });
                """
APPEND_ELEMENT = """
$('#{id}').attr('id','{id}'+'_old');
element.append('<div id="{id}" style="width: 600px;height:400px;"></div>');"""
def generate_new_chartId():
    global i
    i+=1
    return 'charts{}'.format(i)
i = 25
class Chart():
    def __init__(self,**kwargs):
 
        self._chartId = str(uuid.uuid4())
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
    def set_tooltip(self):
        pass
    def get_option(self):
        global optionx
        return option
    def _repr_javascript_(self):
        return (APPEND_ELEMENT.format(id=self._chartId))+\
                (self._get_resync_data_strings(option))
        
        #return RESET_OPTION % (self._chartId,json.dumps(option))
    
        
    
    
    
    
def append(chartId):
    return Javascript("""element.append('<div id="%s" style="width: 600px;height:200px;"></div>');"""%chartId)