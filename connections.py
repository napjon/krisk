#Connection File
from IPython.display import Javascript,HTML

def init_notebook():
    print(Loading JS Script....)
    return Javascript("""
            require.config({
                  paths: {
                      echarts: '//echarts.baidu.com/dist/echarts.min'
                  }
                });""")
