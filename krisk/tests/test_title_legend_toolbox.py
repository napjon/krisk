def test_title(bar_simple):
    # Blank Title
    assert bar_simple.option['title'] == {'text': ''}
    # Title with set position
    c_t = bar_simple.set_title('Hellow', x_pos='auto', y_pos='-5%')
    assert bar_simple.option['title'] == {'left': 'auto',
                                           'text': 'Hellow',
                                           'top': '5%'}


def test_legend(bar_simple):
    # Blank Legend
    assert bar_simple.option['legend'] == {'align': 'auto',
                                           'bottom': 'auto',
                                           'data': [],
                                           'left': 'auto',
                                           'orient': 'horizontal'}

    # Legend with orientation and position
    c_l = bar_simple.set_legend(orient='vertical', x_pos='-5%', y_pos='auto')
    assert bar_simple.option['legend'] == {'align': 'auto',
                                           'bottom': 'auto',
                                           'data': [],
                                           'left': 'auto',
                                           'orient': 'vertical',
                                           'right': '5%'}


def test_toolbox(bar_simple):
    # Default Toolbox
    c_d = bar_simple.option['toolbox']
    assert c_d == {'align': 'auto',
                   'bottom': 'auto',
                   'feature': {'dataZoom': {'show': False, 'title': 'Zoom'},
                    'restore': {'show': False, 'title': 'Reset'}},
                   'left': 'auto',
                   'orient': 'horizontal'}

    # Default Toolbox with Non-Orientation and Position
    c_dop = (bar_simple.set_toolbox(
        align='right', orient='vertical', x_pos='-5%', y_pos='-5%')
             .option['toolbox'])
    assert c_dop == {'align': 'right',
                     'feature': {'dataZoom': {'show': False, 'title': 'Zoom'},
                      'restore': {'show': False, 'title': 'Reset'}},
                     'orient': 'vertical',
                     'right': '5%',
                     'top': '5%'}

    # Restore, Save, and Zoom
    c_rsz = (bar_simple.set_toolbox(
        restore=True, save_format='png', data_zoom=True).option['toolbox'])
    assert c_rsz == {'align': 'auto',
                     'bottom': 'auto',
                     'feature': {'dataZoom': {'show': True,
                                              'title': 'Zoom'},
                                 'restore': {'show': True,
                                             'title': 'Reset'},
                                 'saveAsImage': {'show': True,
                                                 'title': 'Download as Image',
                                                 'type': 'png'}},
                     'left': 'auto',
                     'orient': 'horizontal'}

    # Data View and Magic Type
    c_vzm = (bar_simple.set_toolbox(
        data_view=False, data_zoom=True, magic_type=['line', 'bar'])
             .option['toolbox'])
    assert c_vzm == {'align': 'auto',
                     'bottom': 'auto',
                     'feature': {'dataView': {'lang': ['Table View', 'Back',
                                                       'Modify'],
                                              'readOnly': False,
                                              'show': True,
                                              'title': 'Table View'},
                                 'dataZoom': {'show': True,
                                              'title': 'Zoom'},
                                 'magicType': {'show': True,
                                               'title': 'Chart Options',
                                               'type': ['line', 'bar']},
                                 'restore': {'show': False,
                                             'title': 'Reset'}},
                     'left': 'auto',
                     'orient': 'horizontal'}
