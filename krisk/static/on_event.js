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