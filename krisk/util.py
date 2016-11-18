import os
from warnings import warn


def join_current_dir(file):
    """Join filepath with current file directory"""
    cwd = os.path.dirname(__file__)
    return os.path.join(cwd, file)


def get_content(filepath):
    """Retrieve content from file"""
    abs_path = join_current_dir(filepath)
    with open(abs_path, 'r') as f:
        return f.read()


def init_notebook():
    """
    Inject Javascript to notebook, useful when you provide html notebook
    generated (e.g nbviewwer). You don't have to use this when using
    notebook, as it already provided by nbextension. This function must be
    last executed in a cell to produce Javascript in the output cell
    """
    STATIC_URL = "https://cdn.rawgit.com/napjon/krisk/master/krisk/static"
    ECHARTS_VERSION = "3.2.1"
    ECHARTS_URL = ("https://cdnjs.cloudflare.com/ajax/libs/echarts/{ECHARTS_VERSION}/echarts.min"
                   .format(ECHARTS_VERSION=ECHARTS_VERSION))

    from IPython.display import Javascript
    return Javascript("""
    require.config({{
                 baseUrl : "{STATIC_URL}",
                 paths: {{
                      echarts: "{ECHARTS_URL}"
                  }}
    }});
    """.format(STATIC_URL=STATIC_URL, ECHARTS_URL=ECHARTS_URL))


def future_warning():

    return warn("New feature, possibly breaking changes in future releases",
                FutureWarning)
