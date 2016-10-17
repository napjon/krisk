import krisk.plot as kk


def test_replot_and_resync(bar_simple, df_simple):

    c = bar_simple
    stripped = lambda x: x.data.replace('\n', '').replace(' ', '')
    assert stripped(c.replot(c)) == stripped(c.resync_data(df_simple))


def test_flip(bar_simple):

    assert bar_simple.option['xAxis'] == bar_simple.flip_axes(
    ).option['yAxis']


def test_read_df(gapminder):

    africa = kk.bar(gapminder[gapminder.continent == 'Africa'], 'year')
    asia = africa.read_df(gapminder[gapminder.continent == 'Asia'])
    africa_opt = africa.option
    asia_opt = asia.option

    africa_opt.pop('series')
    asia_opt.pop('series')

    assert africa_opt == asia_opt


def test_color(bar_simple):

    # Set color modify the bar_simple itself! Potentially bug
    colored = bar_simple.set_color(
        background='green', palette=['purple']).option
    assert colored['backgroundColor'] == 'green'
    assert colored['color'] == ['purple']

def test_template(decl_chart):
    assert decl_chart.option['legend']['data'] == []
    assert decl_chart.option['series'][0]['data'] == [10, 3, 7, 4, 5]
    assert decl_chart.option['series'][0]['name'] == 'continent'
    assert decl_chart.option['series'][0]['type'] == 'bar'

    assert decl_chart.option['title']['text'] == ''
    assert decl_chart.option['tooltip']['axisPointer'] == {'type': 'line'}
    assert decl_chart.option['xAxis']['data'] == ['Americas', 'Asia', 'Africa', 'Oceania', 'Europe']
    assert decl_chart.option['yAxis'] == {}

def test_label_axes(decl_chart):
    decl_chart.set_xlabel('xlabel')
    decl_chart.set_ylabel('ylabel')
    assert decl_chart.option['xAxis'] == {'data': ['Americas', 'Asia', 'Africa', 'Oceania', 'Europe'],
                                            'name': 'xlabel',
                                            'nameGap': 30,
                                            'nameLocation': 'middle',
                                            'nameRotate': 0,
                                            'nameTextStyle': {'fontSize': 16}}

    assert decl_chart.option['yAxis'] == {'name': 'ylabel',
                                           'nameGap': 30,
                                           'nameLocation': 'middle',
                                           'nameRotate': 90,
                                           'nameTextStyle': {'fontSize': 16}}