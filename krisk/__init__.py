# Krisk is a module to bridge E-Charts to python data science ecosystem


import krisk.chart.api as chart
import krisk.plot.api as plot
from krisk.chart.api import Chart, rcParams
from krisk.specs import ChartSpec, ClaimSpec, ResearchDraft
from krisk.util import init_notebook

__version__ = "0.9.0"

__all__ = [
    "Chart",
    "ChartSpec",
    "ClaimSpec",
    "ResearchDraft",
    "chart",
    "init_notebook",
    "plot",
    "rcParams",
]


def _jupyter_nbextension_paths():
    return [
        dict(
            section="notebook",
            src="static",  # relative to 'krisk' directory
            dest="krisk",  # directory in "nbextension"
            require="krisk/krisk-require",  # relative to nbextension path
        )
    ]
