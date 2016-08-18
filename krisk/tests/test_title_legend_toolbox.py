import pytest

@pytest.fixture
def chart():
    import pandas as pd
    import krisk.plot as kk
    df = pd.DataFrame({'x': ['a','b','c']})
    return kk.bar(df,'x')

def test_title(chart):
    # Blank Title
    assert chart._option['title'] == {'text': ''}
    # Title with set position
    c_t = chart.set_title('Hellow',x_pos='auto',y_pos='-5%')
    assert chart._option['title'] == {'left': 'auto', 'text': 'Hellow', 'top': '5%'}
    
def test_legend(chart):
    # Blank Legend
    assert chart._option['legend'] == {'data': []}
    
    # Legend with orientation and position
    c_l = chart.set_legend(orient='vertical',x_pos='-5%',y_pos='auto')
    assert chart._option['legend'] =={'align': 'auto',
                                      'bottom': 'auto',
                                      'data': [],
                                      'orient': 'vertical',
                                      'right': '5%'}
    
def test_tolbox(chart):
    # No Toolbox
    assert chart._option.get('toolbox', None) == None
    
    # Default Toolbox
    c_d = chart.set_toolbox()._option['toolbox']
    assert  c_d ==  {'align': 'auto',
                     'bottom': 'auto',
                     'feature': {'dataZoom': {'show': False, 'title': 'Zoom'},
                     'restore': {'show': False, 'title': 'Reset'}},
                     'left': 'auto',
                     'orient': 'horizontal'}
    
    # Default Toolbox with Non-Orientation and Position
    c_dop = (chart
             .set_toolbox(align='right',orient='vertical',x_pos='-5%',y_pos='-5%')
             ._option['toolbox'])
    assert c_dop == {'align': 'right',
                     'feature': {'dataZoom': {'show': False, 'title': 'Zoom'},
                      'restore': {'show': False, 'title': 'Reset'}},
                     'orient': 'vertical',
                     'right': '5%',
                     'top': '5%'}
    
    # Restore, Save, and Zoom
    c_rsz = (chart
             .set_toolbox(restore=True,
                          save_format='png',
                          data_zoom=True)
             ._option['toolbox'])
    assert c_rsz ==  {'align': 'auto',
                      'bottom': 'auto',
                      'feature': {'dataZoom': {'show': True, 'title': 'Zoom'},
                       'restore': {'show': True, 'title': 'Reset'},
                       'saveAsImage': {'show': True,
                                       'title': 'Download as Image',
                                       'type': 'png'}},
                      'left': 'auto',
                      'orient': 'horizontal'}
    
    # Data View and Magic Type
    c_vzm = (chart
             .set_toolbox(data_view=False,
                          data_zoom=True,
                          magic_type=['line','bar'])
             ._option['toolbox'])
    assert c_vzm == {'align': 'auto',
                     'bottom': 'auto',
                     'feature': {'dataView': {'lang': ['Table View',
                                                       'Back',
                                                       'Modify'],
                       'readOnly': False,
                       'show': True,
                       'title': 'Table View'},
                      'dataZoom': {'show': True, 'title': 'Zoom'},
                      'magicType': {'show': True,
                       'title': 'Chart Options',
                       'type': ['line', 'bar']},
                      'restore': {'show': False, 'title': 'Reset'}},
                     'left': 'auto',
                     'orient': 'horizontal'}