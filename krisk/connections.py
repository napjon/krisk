
from collections import OrderedDict
from IPython.display import Javascript
import json

ECHARTS_URL = 'https://cdnjs.cloudflare.com/ajax/libs/echarts/3.2.0/'
ECHARTS_FILE = 'echarts.min'
d_paths = OrderedDict({})
THEMES = ['dark','vintage','roma','shine','infographic','macarons']
THEMES_URL='//echarts.baidu.com/asset/theme/'
PATH_LOCAL = 'js/'


def init_notebook(online=True):
    """Inject Javascript to notebook, default using local js.
    
    """
    return Javascript("""
    require.config({
                 baseUrl : 'krisk/js',
                 paths: {
                     echarts: 'echarts.min'
                 }
    });
    """)
    
def get_paths():
    return ['echarts']
#     return d_paths.keys()