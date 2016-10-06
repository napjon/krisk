# Krisk is a module to bridge E-Charts to python data science ecosystem

from krisk.connections import init_notebook

__version__ = '0.1.11'


def _jupyter_nbextension_paths():
    return [dict(
            section="notebook",
            src="static", # relative to 'krisk' directory
            dest="krisk", # directory in "nbextension"
            require="krisk/krisk-require"  # relative to nbextension path
        )]