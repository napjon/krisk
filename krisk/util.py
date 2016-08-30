import os
from copy import deepcopy


def join_current_dir(file):
    cwd = os.path.dirname(__file__)
    return os.path.join(cwd, file)
