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
