import krisk.plot as kk


def test_replot_and_resync(bar_simple, df_simple):

    c = bar_simple
    stripped = lambda x: x.data.replace('\n', '').replace(' ', '')
    assert stripped(c.replot(c)) == stripped(c.resync_data(df_simple))


def test_flip(bar_simple):

    assert bar_simple.get_option()['xAxis'] == bar_simple.flip_axes(
    ).get_option()['yAxis']


def test_read_df(gapminder):

    africa = kk.bar(gapminder[gapminder.continent == 'Africa'], 'year')
    asia = africa.read_df(gapminder[gapminder.continent == 'Asia'])
    africa_opt = africa.get_option()
    asia_opt = asia.get_option()

    africa_opt.pop('series')
    asia_opt.pop('series')

    assert africa_opt == asia_opt

# Disable this as only testing the script text
# def test_on_event(df_simple):
#     p = kk.bar(df_simple, 'x')

#     def handler_foo(params):
#         return m.resync_data(df_simple)

#     on_event = p.on_event('click', handler_foo)

#     assert on_event._events == {'click': 'handler_foo'}
#     code_handler = on_event._repr_javascript_().split('\n')[-13]
#     input_code = '    var code_input = "import json; handler_foo(json.loads(\'" + json_strings + "\'))";'
#     assert code_handler == input_code


def test_color(bar_simple):

    # Set color modify the bar_simple itself! Potentially bug
    colored = bar_simple.set_color(
        background='green', palette=['purple']).get_option()
    assert colored['backgroundColor'] == 'green'
    assert colored['color'] == ['purple']


def test_label_axes(decl_chart):
    decl_chart.set_xlabel('xlabel')
    decl_chart.set_ylabel('ylabel')
    assert decl_chart.option['xAxis'] == {
        'data': ['Americas', 'Asia', 'Africa', 'Oceania', 'Europe'],
        'name': 'xlabel',
        'nameGap': 30,
        'nameLocation': 'middle',
        'nameRotate': 0,
        'nameTextStyle': {'fontSize': 16}
    }

    assert decl_chart.option['yAxis'] == {'name': 'ylabel',
                                          'nameGap': 30,
                                          'nameLocation': 'middle',
                                          'nameRotate': 90,
                                          'nameTextStyle': {'fontSize': 16}}
