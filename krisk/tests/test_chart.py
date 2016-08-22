
import krisk.plot as kk

def test_flip(bar_simple):
    
    assert bar_simple.get_option()['xAxis'] == bar_simple.flip_axes().get_option()['yAxis']
    
def test_color(bar_simple):
    
    colored = bar_simple.set_color(background='green',palette=['purple']).get_option()
    assert colored['backgroundColor'] == 'green'
    assert colored['color'] == ['purple']
    
def test_read_df(gapminder):
    
    africa = kk.bar(gapminder[gapminder.continent == 'Africa'],'year')
    asia = africa.read_df(gapminder[gapminder.continent == 'Asia'])
    africa_opt = africa.get_option()
    asia_opt = asia.get_option()
    
    africa_opt.pop('series')
    asia_opt.pop('series')
    
    assert africa_opt == asia_opt
    