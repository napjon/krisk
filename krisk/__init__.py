# Krisk is a module to bridge E-Charts to python data science ecosystem


from krisk.util import init_notebook
import krisk.plot.api as plot
# Override chart to prevent all variables to be accessed except two below
import krisk.chart.api as chart
from krisk.chart.api import rcParams, Chart

__version__ = '0.1.11'


def _jupyter_nbextension_paths():
    return [dict(
            section="notebook",
            src="static", # relative to 'krisk' directory
            dest="krisk", # directory in "nbextension"
            require="krisk/krisk-require"  # relative to nbextension path
        )]