ECHARTS_URL = '//echarts.baidu.com/dist/'
ECHARTS_FILE = 'echarts.min'
d_paths = OrderedDict({'echarts':ECHARTS_URL+ECHARTS_FILE})

THEMES = ['dark','vintage','roma','shine','infographic','macarons']
THEMES_URL='//echarts.baidu.com/asset/theme/'
for t in THEMES:
    d_paths[t] =  THEMES_URL+t

def init_notebook():
    return Javascript("""require.config({
                  paths:%s
                   });"""%json.dumps(d_paths))