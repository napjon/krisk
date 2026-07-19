import os
from warnings import warn


def join_current_dir(file):
    """Join filepath with current file directory"""
    cwd = os.path.dirname(__file__)
    return os.path.join(cwd, file)


def get_content(filepath):
    """Retrieve content from file"""
    abs_path = join_current_dir(filepath)
    with open(abs_path) as f:
        return f.read()


def init_notebook():
    """Return a compatibility display object for historical notebooks.

    Krisk 0.9+ embeds its renderer in each chart output, so notebooks work
    offline and no global RequireJS or CDN setup is necessary.
    """
    from IPython.display import Javascript

    return Javascript("/* Krisk 0.9+ charts are self-contained. */")


def future_warning():

    return warn(
        "New feature, possibly breaking changes in future releases",
        FutureWarning,
        stacklevel=2,
    )
