from setuptools import setup, find_packages
from krisk import __version__

setup(
    name='krisk',
    version=__version__,
    description='Echarts Statistical Visualization for Python Data Science',
    author='Jonathan Napitupulu',
    author_email='napitupulu.jon@gmail.com',
    download_url='https://github.com/napjon/krisk/',
    url='https://github.com/napjon/krisk/',
    license='BSD (3-clause)',
    packages=find_packages(),
    package_data={'krisk': ['static/template.html']},
    #                       'static/*.html']}, #Disable first until nbextionsion is available
    classifiers=[
        'Development Status :: 4 - Beta', 'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5'
    ])


def _jupyter_nbextension_paths():
    return [dict(
            section="notebook",
            src="static", #relative to 'krisk' directory
            dest="krisk", # directory in "nbextension"
            require="krisk"
        )]
