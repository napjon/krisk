from krisk.util import join_current_dir


def save_html(script, path):

    from jinja2 import Template

    html_template = open(join_current_dir('static/template.html'), 'r')
    script = script.replace('element', '$("body")')
    f = open(path, 'w')
    f.write(Template(html_template.read()).render(SCRIPT=script))
    f.close()
    html_template.close()


RESET_OPTION = """
require(['echarts', 'dark', 'vintage', 'roma', 'shine', 'infographic', 'macarons'],
function(echarts){{
    
    function parseFunction(str){{
        return eval('(' + str + ')');
    }}
    
    var myChart = echarts.init(document.getElementById("{chartId}"),"{theme}");
    
    var option = {option};
    option['tooltip']['formatter'] = parseFunction(option['tooltip']['formatter']);
    myChart.setOption(option);
    
    {events}
    
}});
"""

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
    // TODO: Import json everytime cell executed is wasteful. json lib needs to be in user session. 
    var code_input = "import json; {function}(json.loads('" + json_strings + "'))";
    console.log("Executing code: " + code_input);
    cell.set_text(code_input);
    cell.execute();
    
    // Immediately delete the cell after execute
    nb.delete_cell();
    
}});
"""
