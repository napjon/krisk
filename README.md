# Overview

Krisk bring Echarts to Python Data Science Ecosystem, and helpful tools for high level statistical interactive visualization.

![jpg] (https://raw.githubusercontent.com/napjon/krisk/master/notebooks/img/readme.jpg)

# Dependencies

* Python 3.5 (Python 2.7 should be supported, haven't test it yet)
* Jupyter Notebook 4.2.x
* Pandas 0.18.x
* Echarts 3.2.1 (built-in)

# Install
```Python
pip install jupyter pandas krisk
```


# Tutorials

* [Introduction](http://nbviewer.jupyter.org/github/napjon/krisk/blob/master/notebooks/Intro.ipynb)
* [Themes and Colors](http://nbviewer.jupyter.org/github/napjon/krisk/blob/master/notebooks/themes-colors.ipynb)
* [Legend, Title, and Toolbox](http://nbviewer.jupyter.org/github/napjon/krisk/blob/master/notebooks/legend-title-toolbox.ipynb)
* [Resync Data and Reproducible Charts](http://nbviewer.jupyter.org/github/napjon/krisk/blob/master/notebooks/resync-reproducible.ipynb)


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
