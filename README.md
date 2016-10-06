WARNING:
This is a development branch of 0.2. For more stable version, please use master branch.

The version of 0.2 will 

* Provide more complex chart type from cheatsheet originally created by A. Abela http://extremepresentation.typepad.com/files/choosing-a-good-chart-09.pdf
  * Support Waterfall for [type 1](http://echarts.baidu.com/demo.html#bar-waterfall) and [type 2](http://echarts.baidu.com/demo.html#bar-waterfall2)
  * 100%  for stacked bar and stacked line chart
  * Provide smooth line for histogram and all type of line chart as well
  * Add Python 2.7 Compatibility
  * Add offline js as nbextension (optional)
  * Add Diverging, Sequential, and Qualitative mode for bar chart

The `plot.py` will also evolve into package. Scatter and bar-line chart must be separated, because it's clear that both must be treated differently.
```
plot/
 __init__.py (API, previously plot.py)
 make_chart.py
 scatter.py
 bar_line.py
```


[![CircleCI](https://circleci.com/gh/napjon/krisk.svg?style=shield)](https://circleci.com/gh/napjon/krisk) 
[![PyPI version](https://badge.fury.io/py/krisk.svg)](https://pypi.python.org/pypi/krisk/)
[![Coverage Status](https://img.shields.io/codecov/c/github/napjon/krisk/master.svg)](https://codecov.io/gh/napjon/krisk)
![svg](https://img.shields.io/github/license/napjon/krisk.svg)

# Overview

Krisk bring Echarts to Python Data Science Ecosystem, and helpful tools for high level statistical interactive visualization.

![jpg] (https://raw.githubusercontent.com/napjon/krisk/master/readme.jpg)

# Dependencies

* Python 3.5 (Python 2.7 should be supported, haven't test it yet)
* Jupyter Notebook 4.2.x
* Pandas 0.18.x
* Echarts 3.2.1 (built-in)

# Install
```Python
pip install jupyter pandas krisk
jupyter nbextension install --py krisk --sys-prefix
jupyter nbextension enable  --py krisk --sys-prefix
```


# Tutorials

* [Introduction](http://nbviewer.jupyter.org/github/napjon/krisk/blob/master/notebooks/Intro.ipynb)
* [Themes and Colors](http://nbviewer.jupyter.org/github/napjon/krisk/blob/master/notebooks/themes-colors.ipynb)
* [Legend, Title, and Toolbox](http://nbviewer.jupyter.org/github/napjon/krisk/blob/master/notebooks/legend-title-toolbox.ipynb)
* [Resync Data and Reproducible Charts](http://nbviewer.jupyter.org/github/napjon/krisk/blob/master/notebooks/resync-reproducible.ipynb)
* [Declarative Visualization](http://nbviewer.jupyter.org/github/napjon/krisk/blob/master/notebooks/declarative-visualization.ipynb)


# What It Does

* Chart Integration with Jupyter Notebook, widgets, and Dashboard.
* Statistical interactive visualization
* Ability backed by Echarts (Toolbox, Transition, Tooltip, etc.)

# What It Doesn't Do

Krisk won't implement all features of Echarts. For more advanced usage, Krisk users can use JSON `option` (or HTML) output produced by Krisk to optimize in Javascript. 

Only basic charts are supported for explanation visualization.  The plan will support:

* More complex line, bar, scatter, and histogram.
* Geoscatter plot
* Time Series

Of course, contributions are welcome to support all chart types and advanced features.

# Motivation for Another Visualization Library

Krisk is targeted for building interactive dashboard application on top of two key components of Jupyter framework, [ipywidgets](https://ipywidgets.readthedocs.io/en/latest/) and [Jupyter Dashboard](https://github.com/jupyter-incubator/dashboards).

Krisk is also act as tool to support reproducible chart by utilizing pandas DataFrame as data input.

# License

New BSD
