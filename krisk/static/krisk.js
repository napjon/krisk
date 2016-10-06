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


