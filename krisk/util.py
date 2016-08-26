def join_current_dir(file):
    import os
    cwd = os.path.dirname(__file__)
    return os.path.join(cwd, file)
