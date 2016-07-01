
from collections import OrderedDict
from IPython.display import Javascript
import json

ECHARTS_URL = '//echarts.baidu.com/dist/'
ECHARTS_FILE = 'echarts.min'
d_paths = OrderedDict({'echarts':ECHARTS_URL+ECHARTS_FILE})
# d_paths['JSONfn'] = '//raw.githubusercontent.com/vkiryukhin/jsonfn/master/jsonfn'

THEMES = ['dark','vintage','roma','shine','infographic','macarons']
THEMES_URL='//echarts.baidu.com/asset/theme/'
PATH_LOCAL = 'js/'


def init_notebook(online=True):
    """Inject Javascript to notebook, default using local js.
    
    """
    global d_paths
    if online:
        ec_path,themes_path =ECHARTS_URL,THEMES_URL
    else:
        ec_path = themes_path = PATH_LOCAL
        
    d_paths = OrderedDict({'echarts':ec_path+ECHARTS_FILE})
    
    for t in THEMES:
        d_paths[t] =  themes_path+t    
    
    return Javascript("""require.config({
                  paths:%s
                   });"""%json.dumps(d_paths,indent=4))
def get_paths():
    return d_paths.keys()