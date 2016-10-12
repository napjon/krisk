import os
from copy import deepcopy
import codecs


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
    Inject Javascript to notebook, useful when you provide html notebook generated (e.g nbviewwer).
    You don't have to use this when using notebook, as it already provided by nbextension.
    This function must be last executed in a cell to produce Javascript in the output cell    
    """
    from IPython.display import Javascript
    return Javascript("""
    require.config({
                 baseUrl : "//cdn.rawgit.com/napjon/krisk/master/krisk/static",
                 paths: {
                      echarts: "//cdnjs.cloudflare.com/ajax/libs/echarts/3.2.1/echarts.min"
                  }
    });
    """)